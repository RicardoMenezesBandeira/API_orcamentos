from flask import Flask, request, jsonify, redirect, render_template, send_from_directory, url_for
from werkzeug.utils import secure_filename  # sanitiza nomes de arquivos
from flask_cors import CORS
import os
import json
from login import token_required, create_token, logon
from weasyprint import HTML
from gerar_templates.preenche_template import preencher_template

# CONFIGURAÇÃO DO FLASK
app = Flask(
    __name__,
    template_folder="template",
    static_folder="static"
)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config['SECRET_KEY'] = 'meusegredosecreto'

# ================================
# Rotas existentes (sem alterações)
# ================================
@app.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    username = auth.get("username")
    password = auth.get("password")
    return logon(username, password, app.config['SECRET_KEY'])

@app.route("/postTemplate", methods=['POST'])
def receber_orcamento():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        dados = request.get_json(force=True)
        if not dados:
            return jsonify({"erro": "JSON não fornecido"}), 400

        # Salvamento incremental de JSONs de orçamentos
        pasta = "bd/json_preenchimento"
        os.makedirs(pasta, exist_ok=True)
        arquivos = [f for f in os.listdir(pasta) if f.endswith(".json")]
        numeros = [int(f.split(".")[0]) for f in arquivos if f.split(".")[0].isdigit()]
        proximo_numero = max(numeros) + 1 if numeros else 1
        nome_arquivo = f"{proximo_numero}.json"
        caminho_arquivo = os.path.join(pasta, nome_arquivo)

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

        return jsonify({"mensagem": "Orçamento salvo com sucesso!"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/verification", methods=["GET"])
def verificar_template():
    json_dir = "bd/json_preenchimento"
    json_files = sorted(
        [f for f in os.listdir(json_dir) if f.endswith(".json")],
        key=lambda f: os.path.getmtime(os.path.join(json_dir, f))
    )
    if not json_files:
        return "Nenhum JSON encontrado", 404

    json_path = os.path.join(json_dir, json_files[-1])
    with open(json_path, "r", encoding="utf-8") as f:
        dados = json.load(f)

    nome_id = dados.get("nome", "usuario")
    templates = dados.get("templates", [])
    if not templates:
        return "Nenhum template selecionado", 400

    primeiro_template = templates[0]
    base_path = f"gerar_templates/{primeiro_template}"
    template_html = os.path.join(base_path, "template_corrigido_windows1252.htm")
    destino_html = os.path.join(base_path, f"preenchido_{nome_id}.htm")

    preencher_template(template_html, destino_html, dados)
    iframe_src = f"/template_preenchido/{primeiro_template}/preenchido_{nome_id}.htm"
    return render_template("revisao.html", iframe_src=iframe_src, template_nome=primeiro_template)

@app.route('/template_preenchido/<template>/<arquivo>')
def servir_template_preenchido(template, arquivo):
    caminho = f"gerar_templates/{template}"
    return send_from_directory(caminho, arquivo)

# ================================
# Configuração de persistência para empresas
# ================================
EMPRESAS_JSON = os.path.join("bd", "empresas.json")
# Garante existência do diretório e arquivo
os.makedirs(os.path.dirname(EMPRESAS_JSON), exist_ok=True)
if not os.path.exists(EMPRESAS_JSON):
    with open(EMPRESAS_JSON, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2, ensure_ascii=False)

# Diretórios para armazenar uploads
LOGO_DIR = os.path.join(app.static_folder, "logos")
os.makedirs(LOGO_DIR, exist_ok=True)
TEMPLATE_ORC_DIR = os.path.join(app.static_folder, "templates_orcamento")
os.makedirs(TEMPLATE_ORC_DIR, exist_ok=True)

# Função para salvar novo registro de empresa
def salvar_empresa(registro: dict):
    try:
        with open(EMPRESAS_JSON, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        dados = []
    dados.append(registro)
    with open(EMPRESAS_JSON, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

# ================================
# Rota GET/POST para cadastro de empresas
# ================================
@app.route("/empresas/cadastro", methods=["GET", "POST"])
def cadastrar_empresa():
    if request.method == "POST":
        nome = request.form.get("nome")
        endereco = request.form.get("endereco")
        cnpj = request.form.get("cnpj")
        tipo_imposto = request.form.get("tipo_imposto")
        logo_file = request.files.get("logo")
        template_file = request.files.get("template_orcamento")

        logo_path = None
        if logo_file and logo_file.filename:
            logo_filename = secure_filename(logo_file.filename)
            logo_dest = os.path.join(LOGO_DIR, logo_filename)
            logo_file.save(logo_dest)
            logo_path = f"logos/{logo_filename}"

        template_path = None
        if template_file and template_file.filename:
            temp_filename = secure_filename(template_file.filename)
            temp_dest = os.path.join(TEMPLATE_ORC_DIR, temp_filename)
            template_file.save(temp_dest)
            template_path = f"templates_orcamento/{temp_filename}"

        salvar_empresa({
            "nome": nome,
            "endereco": endereco,
            "cnpj": cnpj,
            "tipo_imposto": tipo_imposto,
            "logo": logo_path,
            "template_orcamento": template_path
        })
        return redirect(url_for('cadastrar_empresa'))

    return render_template("cadastro_empresas.html")

# ================================
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-access-token')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

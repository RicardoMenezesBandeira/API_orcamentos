from flask import Flask, request, jsonify, send_file, redirect, render_template, send_from_directory
from weasyprint import HTML
from login import token_required, create_token, logon
from flask_cors import CORS
import os
import json
from gerar_templates.preenche_template import preencher_template

#testeee

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config['SECRET_KEY'] = 'meusegredosecreto'


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

        print("Orçamento recebido:")
        for chave, valor in dados.items():
            print(f"{chave}: {valor}")

        # Salvar JSON no disco com nome incremental
        pasta = "bd/json_preenchimento"
        os.makedirs(pasta, exist_ok=True)
        arquivos = [f for f in os.listdir(pasta) if f.endswith(".json")]
        numeros = [int(f.split(".")[0]) for f in arquivos if f.split(".")[0].isdigit()]
        proximo_numero = max(numeros) + 1 if numeros else 1
        nome_arquivo = f"{proximo_numero}.json"
        caminho_arquivo = os.path.join(pasta, nome_arquivo)

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

        print(f"Orçamento salvo em: {caminho_arquivo}")

        
        return jsonify({"mensagem": "Orçamento salvo com sucesso!"}), 200


    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    

@app.route("/verification", methods=["GET"])
def verificar_template():
    # Pega o JSON mais antigo
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

    # Preenche o template
    preencher_template(template_html, destino_html, dados)

    # Cria o caminho do iframe que será injetado na página
    iframe_src = f"/template_preenchido/{primeiro_template}/preenchido_{nome_id}.htm"

    return render_template("revisao.html", iframe_src=iframe_src, template_nome=primeiro_template)

@app.route('/template_preenchido/<template>/<arquivo>')
def servir_template_preenchido(template, arquivo):
    caminho = f"gerar_templates/{template}"
    return send_from_directory(caminho, arquivo)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-access-token')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response
if __name__ == "__main__":
    app.config.from_mapping(SECRET_KEY='meusegredosecreto')
    app.run(host="0.0.0.0", port=8000, debug=True)

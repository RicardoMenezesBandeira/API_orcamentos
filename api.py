from flask import Flask, request, jsonify, redirect, render_template,send_file, send_from_directory, url_for
from werkzeug.utils import secure_filename  # sanitiza nomes de arquivos
from flask_cors import CORS
import os
import json
from login import token_required,clean_tolkens, create_token, logon
#testeee

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config['SECRET_KEY'] = 'meusegredosecreto'

@app.route("/")
def login_page():
    return render_template('login.html')
@app.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    username = auth.get("username")
    password = auth.get("password")

    token =logon(username, password, app.config['SECRET_KEY'])["token"]

     # Cria uma resposta combinando JSON e cookie
    response = make_response(jsonify({
        'message': 'Login bem-sucedido',
        'user': username
    }))
    # Configura o cookie seguro
    response.set_cookie(
        'auth_token', 
        token,
        httponly=True,      # Acessível apenas pelo servidor
        secure=True,        # Envia apenas em HTTPS
        samesite='Strict',  # Proteção contra CSRF
        max_age=3600        # Expira em 1 hora
    )
    return response

@app.route("/preencher")
@token_required
def preencher(user_data):
    return render_template("geradorOrcamento.html")

@app.route("/postTemplate", methods=['GET','POST'])
def receber_orcamento():
    if request.method == 'OPTIONS':
        return '', 200
    if request.method == 'GET':
        return render_template("geradorOrcamento.html")
    try:
        dados = request.get_json(force=True)
        # Salvamento incremental de JSONs de orçamentos
        pasta = "bd/json_preenchimento"
        os.makedirs(pasta, exist_ok=True)
        arquivos = [f for f in os.listdir(pasta) if f.endswith(".json")]
        numeros = [int(f.split(".")[0]) for f in arquivos if f.split(".")[0].isdigit()]
        proximo_numero = max(numeros) + 1 if numeros else 1
        nome_arquivo = f"{proximo_numero}.json"
        caminho_arquivo = os.path.join(pasta, nome_arquivo)

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)  # force=True para garantir que o JSON seja analisado mesmo se o cabeçalho não estiver definido
        return jsonify({"mensagem":  dados}), 200

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
    templates = dados.get("templates", [])
    if isinstance(templates, str):
        templates = [templates]
    if not templates:
        return "Nenhum template selecionado", 400

    template_idx = int(request.args.get("template_idx", 0))

    if template_idx >= len(templates):
        return "<h2>Todos os templates foram revisados!</h2><a href='/postTemplate'>Voltar para Início</a>", 200

    empresa = templates[template_idx]
    iframe_src = f"/template_preenchido/{empresa}/proposta_{empresa}_preenchida.htm"


    proximo_idx = template_idx + 1  # Já calcula o próximo

    return render_template(
        "revisao.html",
        iframe_src=iframe_src,
        template_nome=empresa,
        proximo_idx=proximo_idx
    )

@app.route("/dashboard", methods=['GET'])
@token_required
def get_dashboard(user_data):  # Recebe user_data do decorador
    try:
        # Agora você pode acessar todos os dados do usuário
        telefone = user_data.get("telefone")
        nome = user_data.get("nome")
        cargo = user_data.get("cargo")
        user_data=f"telefone: {telefone},nome: {nome},cargo: {cargo}"
        # Faça o processamento necessário aqui
        # Exemplo: buscar templates específicos para este usuário
        template = render_template('index.html', info=user_data)
        return template, 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/getTemplate", methods=['POST']) 
def get_template():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        return send_file('orcamento.pdf', as_attachment=True)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-access-token')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

if __name__ == "__main__":
    app.config.from_mapping(SECRET_KEY='meusegredosecreto')
    app.run(host="0.0.0.0", port=8000, debug=True)

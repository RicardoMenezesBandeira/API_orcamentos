from flask import Flask, request, jsonify, redirect, render_template,send_file, send_from_directory, url_for,make_response
from werkzeug.utils import secure_filename  # sanitiza nomes de arquivos
from flask_cors import CORS
import os
import json
from login import token_required,clean_tolkens, create_token, logon
from cadastra import cadastrar

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

@app.route("/postTemplate", methods=['GET', 'POST'])
def receber_orcamento():
    if request.method == 'OPTIONS':
        return '', 200
    if request.method == 'GET':
        return render_template("geradorOrcamento.html")
    try:
        dados = request.get_json(force=True)

        # 1. Salvamento incremental do JSON
        pasta_json = "bd/json_preenchimento"
        os.makedirs(pasta_json, exist_ok=True)
        arquivos = [f for f in os.listdir(pasta_json) if f.endswith(".json")]
        numeros = [int(f.split(".")[0]) for f in arquivos if f.split(".")[0].isdigit()]
        proximo_numero = max(numeros) + 1 if numeros else 1
        nome_arquivo_json = f"{proximo_numero}.json"
        caminho_arquivo_json = os.path.join(pasta_json, nome_arquivo_json)

        with open(caminho_arquivo_json, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

        # 2. Injeção dos dados em múltiplos templates
        templates = dados.get("templates", [])
        if isinstance(templates, str):
            templates = [templates]

        pasta_templates = "template-PDF"  # Está na raiz do projeto
        os.makedirs(pasta_templates, exist_ok=True)

        for empresa in templates:
            nome_template = f"{empresa.lower()}_placeholders.html"
            caminho_template = os.path.join(pasta_templates, nome_template)

            if not os.path.exists(caminho_template):
                continue  # Se não encontrar, ignora

            with open(caminho_template, "r", encoding="utf-8") as f:
                conteudo_html = f.read()

            # Substituir placeholders
            for chave, valor in dados.items():
                conteudo_html = conteudo_html.replace(f"{{{chave}}}", str(valor))

            # Nome final do orçamento preenchido
            nome_arquivo_saida = f"orcamento_{str(proximo_numero).zfill(3)}_{empresa.lower()}.html"
            caminho_arquivo_saida = os.path.join(pasta_templates, nome_arquivo_saida)

            with open(caminho_arquivo_saida, "w", encoding="utf-8") as f:
                f.write(conteudo_html)

        return jsonify({"mensagem": f"Orçamentos salvos para {', '.join(templates)}."}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500



@app.route("/verification", methods=["GET"])
def verificar_template():
    try:
        # 1. Buscar o último JSON para obter o ID correto
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

        # 2. Pegar templates selecionados
        templates = dados.get("templates", [])
        if isinstance(templates, str):
            templates = [templates]

        if not templates:
            return "Nenhum template selecionado", 400

        # 3. Saber qual template estamos revisando
        template_idx = int(request.args.get("template_idx", 0))

        if template_idx >= len(templates):
            return "<h2>Todos os templates foram revisados!</h2><a href='/postTemplate'>Voltar para Início</a>", 200

        empresa = templates[template_idx]

        # 4. Calcular o ID do orçamento
        id_orcamento = max([int(f.split(".")[0]) for f in os.listdir(json_dir) if f.endswith(".json")])

        # 5. Montar o path relativo do orçamento preenchido
        nome_arquivo_html = f"orcamento_{str(id_orcamento).zfill(3)}_{empresa.lower()}.html"
        iframe_src = f"/template-PDF/{nome_arquivo_html}"
        print(nome_arquivo_html)
        proximo_idx = template_idx + 1

        return render_template(
            "revisao.html",
            iframe_src=iframe_src,
            template_nome=empresa,
            proximo_idx=proximo_idx
        )
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    



@app.route("/template-PDF/<path:filename>")
def servir_template_pdf(filename):
    return send_from_directory("template-PDF", filename)



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

@app.route("/cadastro")
@token_required
def cadastro_page(user_data):
    return render_template('cadastro_usuario.html')

@app.route("/add_usuario", methods=['POST'])
@token_required
def add_usuario(user_data):
    data = request.get_json()
    if (cadastrar(data)):
        return jsonify({"message": "Usuário adicionado com sucesso!"}), 200
    else:
        return jsonify({"message": "Erro ao adicionar usuário!"}), 500

@app.route("/usuario", methods=['GET'])
@token_required
def usuario_page(user_data):
    # Caminho da pasta onde estão os JSONs
    diretorio = './bd/funcionarios'

    # Lista para guardar todos os dados
    todos_os_dados = []

    # Percorre todos os arquivos da pasta
    for nome_arquivo in os.listdir(diretorio):
        if nome_arquivo.endswith('.json'):
            caminho_completo = os.path.join(diretorio, nome_arquivo)
            with open(caminho_completo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                todos_os_dados.append(dados)
    return todos_os_dados
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-access-token')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

if __name__ == "__main__":
    app.config.from_mapping(SECRET_KEY='meusegredosecreto')
    app.run(host="0.0.0.0", port=8000, debug=True)

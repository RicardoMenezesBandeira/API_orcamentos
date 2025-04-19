from flask import Flask, request, jsonify, send_file, render_template,make_response
from weasyprint import HTML
from login import token_required, clean_tolkens, logon
from flask_cors import CORS
import os
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

@app.route("/postTemplate", methods=['POST'])
def receber_orcamento():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        dados = request.get_json(force=True)  # force=True para garantir que o JSON seja analisado mesmo se o cabeçalho não estiver definido
        return jsonify({"mensagem":  dados}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

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

@app.route("/getPDF", methods=['POST']) 
def get_pdf():
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

@app.route("/clear", methods=["POST"])
def clear():
    clean_tolkens()
    # Limpa os tokens armazenados (opcional, dependendo de como você está gerenciando os tokens)
    return "Limpeza realizada com sucesso", 200
    pass
@app.route('/debug', methods=['GET'])
def debug():
    return {
        "template_exists": os.path.exists(os.path.join(app.template_folder, 'index.html')),
        "static_exists": os.path.exists(os.path.join(app.static_folder, 'index.html'))
    }
if __name__ == "__main__":
    app.config.from_mapping(SECRET_KEY='meusegredosecreto')
    app.run(host="0.0.0.0", port=8000, debug=True)

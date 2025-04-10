from flask import Flask, request, jsonify, send_file
from weasyprint import HTML
from login import token_required, create_token, logon
from flask_cors import CORS

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
        dados = request.get_json(force=True)  # force=True para garantir que o JSON seja analisado mesmo se o cabeçalho não estiver definido
        if not dados:
            return jsonify({"erro": "JSON não fornecido"}), 400
        print("Dados recebidos:", dados)
        # Verifica se o JSON contém os campos necessários

        # Aqui você pode fazer o que quiser com os dados — salvar, processar, etc.
        print("Orçamento recebido:")
        for chave, valor in dados.items():
            print(f"{chave}: {valor}")

        return jsonify({"mensagem": "Orçamento recebido com sucesso!", "dadosRecebidos": dados}), 200

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

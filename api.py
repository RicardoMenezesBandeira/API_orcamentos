from flask import Flask, request, jsonify, send_file
from weasyprint import HTML
from login import token_required, create_token, USERS
from flask_cors import CORS

#testeee

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SECRET_KEY'] = 'meusegredosecreto'

@app.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    username = auth.get("username")
    password = auth.get("password")

    if USERS.get(username) == password:
        token = create_token(username, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return jsonify({'message': 'Credenciais inválidas'}), 401

@app.route("/", methods=["GET"])
@token_required
def read_root():
    return jsonify({"message": "Bem-vindo à API protegida!"})

@app.route("/items/<int:item_id>", methods=["GET"])
@token_required
def read_item(item_id):
    return jsonify({"item_id": item_id})

@app.route("/generate_pdf", methods=["GET"])
@token_required
def generate_pdf():
    html_content = """
    <html>
    <head><title>PDF Example</title></head>
    <body><h1>Este é um PDF gerado pela API!</h1></body>
    </html>
    """
    pdf_path = "output.pdf"
    HTML(string=html_content).write_pdf(pdf_path)
    
    return send_file(pdf_path, as_attachment=True)

@app.route("/postTemplate, methods=['POST', 'OPTIONS']")
def receber_orcamento():
    
    try:
        if True:
            pass 
        if request.method == 'OPTIONS':
            return '', 200  # resposta rápida pro preflight
        dados = request.get_json()
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

if __name__ == "__main__":
    app.config.from_mapping(SECRET_KEY='meusegredosecreto')
    app.run(host="0.0.0.0", port=8000, debug=True)

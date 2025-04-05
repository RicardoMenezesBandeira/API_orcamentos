from flask import Flask, request, jsonify, send_file
from weasyprint import HTML
from login import token_required, create_token, USERS

app = Flask(__name__)
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

if __name__ == "__main__":
    app.config.from_mapping(SECRET_KEY='meusegredosecreto')
    app.run(host="0.0.0.0", port=8000, debug=True)

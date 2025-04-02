from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def read_root():
    return jsonify({"message": "Bem-vindo à API!"})

@app.route("/items/<int:item_id>", methods=["GET"])
def read_item(item_id):
    return jsonify({"item_id": item_id})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

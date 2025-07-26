from flask import request, jsonify, current_app
from functools import wraps
import jwt, json, os

TOKENS = []                       # memória volátil

def _load_users():
    with open("bd/funcionarios.json", encoding="utf-8") as f:
        return json.load(f)

def create_token(username: str, secret: str):
    return jwt.encode({"user": username}, secret, algorithm="HS256")

def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return "", 200
        token = request.headers.get("Authorization") or request.cookies.get("auth_token")
        if not token:
            return jsonify({"message": "Token é necessário"}), 401

        try:
            payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            username = payload["user"]
            users = _load_users()
            if username not in users:
                return jsonify({"message": "Usuário não encontrado"}), 401

            user_file = os.path.join("bd", "funcionarios", f"{username}.json")
            user_data = json.load(open(user_file)) if os.path.exists(user_file) else {"nome": username}
            return fn(user_data=user_data, *args, **kwargs)
        except Exception as e:
            return jsonify({"message": f"Erro na autenticação: {e}"}), 401
    return wrapper

def logon(username: str, senha: str, secret: str):
    users = _load_users()
    if username in users and users[username]["senha"] == senha:
        token = create_token(username, secret)
        TOKENS.append({"username": username, "token": token})
        return {"token": token, "user": username}
    return {"token": "erro", "user": "erro"}

def logout():
    token = request.headers.get("Authorization") or request.cookies.get("auth_token")
    TOKENS[:] = [t for t in TOKENS if t["token"] != token]
    return True

def clean_tokens():
    TOKENS.clear()

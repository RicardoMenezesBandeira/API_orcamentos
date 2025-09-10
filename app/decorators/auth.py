from flask import request, jsonify, current_app
from functools import wraps
import jwt, json, os
from pathlib import Path
TOKENS = []                       # memória volátil
BASE_DIR = Path("/app")  # ALTERADO

def _load_users():
    with open(BASE_DIR / "bd" / "funcionarios.json", encoding="utf-8") as f: 
        return json.load(f)

def create_token(username: str, secret: str):
    token = jwt.encode({"user": username}, secret, algorithm="HS256")
    print(f"Token criado para {username}: {token}")
    return token

def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return "", 200
        token = request.headers.get("Authorization") or request.cookies.get("auth_token")
        #if not token:
            #return "", 200
            #return jsonify({"message": "Token é necessário"}), 401

  
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        print(f"Payload decodificado: {payload}")
        username = payload["user"]
        users = _load_users()
        if username not in users:
            return jsonify({"message": "Usuário não encontrado"}), 401

        user_file = BASE_DIR / "bd" / "funcionarios" / f"{username}.json"
        print(f"Carregando dados do usuário de: {user_file}")
        #user_data = json.load(open(user_file)) if os.path.exists(user_file) else {"nome": username}
        if user_file.exists():  # ALTERADO
            user_data = json.load(user_file.open(encoding="utf-8"))  # ALTERADO
        else:
            user_data = {"nome": username}
        print(f"Dados do usuário: {user_data}" )
        return fn(user_data=user_data, *args, **kwargs)
        
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

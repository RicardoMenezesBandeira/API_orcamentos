# auth.py
from flask import request, jsonify
from functools import wraps
import jwt
import datetime
import json
import os 

USERS = json.load(open('bd/funcionarios.json', 'r'))  # Load users from a JSON file
USERS_TOKENS=[]

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return '', 200

        token = request.headers.get('Authorization') or request.cookies.get('auth_token')

        if not token:
            return jsonify({'message': 'Token é necessário'}), 401

        try:
            decoded_token = jwt.decode(token, 'meusegredosecreto', algorithms=["HS256"])
            username = decoded_token['user']
            
            # Verifica se o usuário existe no arquivo principal
            if username not in USERS:
                return jsonify({'message': 'Usuário não encontrado'}), 401
                
            user = USERS[username]
            user_file_path = f'bd/funcionarios/{user}.json'

            # Carrega os dados adicionais do usuário
            if os.path.exists(user_file_path):
                with open(user_file_path, 'r') as file:
                    user_data = json.load(file)
            else:
                user_data = {"erro": "Arquivo de usuário não encontrado", "nome": username}
            
            # Passa os dados do usuário para a função decorada
            return f(user_data=user_data, *args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado', 'redirect': '/'}), 401

        except Exception as e:
            return jsonify({'message': f'Erro na autenticação: {str(e)}'}), 401
    return decorated

def create_token(username, secret_key):
    token = jwt.encode({
        'user': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }, secret_key, algorithm='HS256')
    return token

def logon(username, password, secret_key):  
    user_data = USERS.get(username)
    print(user_data)
    print(password)
    if user_data and user_data["senha"] == password:  # Verifica usuário e senha
        token = create_token(username, secret_key)
        # Se quiser armazenar tokens (opcional, mas geralmente tokens JWT são stateless)
        USERS_TOKENS.append({"username": username, "token": token})
        print(USERS_TOKENS)
        return {
            "token": token, 
            "user": username
        }
    return {"message": "Credenciais inválidas"}
def clean_tolkens():
    USERS_TOKENS.clear()  # Limpa a lista de tokens armazenados


def logout():
    token = request.headers.get('Authorization') or request.cookies.get('auth_token')

    if not token:
        return jsonify({'message': 'Token não fornecido'}), 400

    # Procura o token na lista USERS_TOKENS e remove
    for entry in USERS_TOKENS:
        if entry["token"] == token:
            USERS_TOKENS.remove(entry)
            return True

    return True

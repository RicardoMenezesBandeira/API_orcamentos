# auth.py
from flask import request, jsonify
from functools import wraps
import jwt
import datetime
import json
USERS = json.load(open('bd/funcionarios.json', 'r'))  # Load users from a JSON file

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token é necessário'}), 401

        try:
            token = token.split()[1]  # Remove 'Bearer '
            jwt.decode(token, 'meusegredosecreto', algorithms=["HS256"])
        except Exception as e:
            return jsonify({'message': 'Token inválido ou expirado'}), 401

        return f(*args, **kwargs)
    return decorated

def create_token(username, secret_key):
    token = jwt.encode({
        'user': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }, secret_key, algorithm='HS256')
    return token
def logon(username, password,secret_key):
    if USERS.get(username) == password:
        token = create_token(username,secret_key)
        return jsonify({'token': token})
    return jsonify({'message': 'Credenciais inválidas'}), 401
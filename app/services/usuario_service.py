"""Service layer para operações de usuários (funcionários).
Mantém nomes iguais aos usados no api.py original: cadastrar_usuario, get_usuario, delete_usuario.
"""

from pathlib import Path
import json
import os
from typing import Tuple, Any
from flask import jsonify, request

from ..utils.helpers import get_data
from cadastra import cadastrar


BASE_DIR   = Path(__file__).resolve().parents[2]
BD_DIR     = BASE_DIR / "bd"
FUNC_DIR   = BD_DIR / "funcionarios"
LIST_FILE  = BD_DIR / "funcionarios.json"

FUNC_DIR.mkdir(parents=True, exist_ok=True)



# ---------------------------------------------------------------------------
# A) cadastrar_usuario  (POST /add_usuario)
# ---------------------------------------------------------------------------

def cadastrar(data):
    
    usuario = {
    "nome": data["nome"],
    "telefone":data["telefone"],
    "user":data["user"],
    "admin":data["admin"]
}
    login = {
    "user": data["user"],
    "senha": data["senha"]
    }
    print(usuario) 
    print(login)
    try:
        # Diretório onde o arquivo será salvo
        diretorio = f'./bd/funcionarios/'

        # Verifica se o diretório existe, se não, cria
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)

        with open(f'./bd/funcionarios/{login["user"]}.json', 'w', encoding='utf-8') as f:
            json.dump(usuario, f, indent=4, ensure_ascii=False)
        # Tenta carregar a lista de funcionários, se o arquivo não existir ou estiver vazio, cria uma lista vazia
        try:
            with open(f'./bd/funcionarios.json', 'r', encoding='utf-8') as f:
                funcionarios = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):  # Se não encontrar o arquivo ou estiver vazio
            funcionarios = []
        
        # Adiciona o novo usuário à lista de funcionários
        user = login["user"]
        print(funcionarios)
        if user in funcionarios:
            print("Usuario já existe")
        else:
            print ("Usuario não existe")
            senha = login["senha"]        
            funcionarios[user] = {"senha":senha}
        # Salva a lista atualizada de funcionários
        with open(f'./bd/funcionarios.json', 'w', encoding='utf-8') as f:
            json.dump(funcionarios, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao cadastrar usuário: {str(e)}")
        return {"erro": str(e)}, 500
    return True




# ---------------------------------------------------------------------------
# B) get_usuario  (GET /usuario)
# ---------------------------------------------------------------------------

def get_usuario() -> Tuple[list[Any], int]:
    usuarios = []
    for arq in FUNC_DIR.glob("*.json"):
        with arq.open(encoding="utf-8") as f:
            try:
                usuarios.append(json.load(f))
            except json.JSONDecodeError:
                continue
    return usuarios, 200

# ---------------------------------------------------------------------------
# C) delete_usuario  (DELETE /delete_usuario/<username>)
# ---------------------------------------------------------------------------

def delete_usuario(username: str, current_user: dict) -> Tuple[dict, int]:
    username = username.lower()
    if current_user.get("user") == username:
        return {"error": "Você não pode excluir a si mesmo!"}, 401

    user_file = FUNC_DIR / f"{username}.json"
    if not user_file.exists():
        return {"error": f"Arquivo do usuário '{username}' não encontrado."}, 404

    try:
        user_file.unlink()
    except Exception:
        return {"error": "Erro ao apagar arquivo de usuário."}, 500

    # Atualiza lista geral
    try:
        if LIST_FILE.exists():
            all_users = json.loads(LIST_FILE.read_text(encoding="utf-8"))
        else:
            all_users = {}
        if username in all_users:
            del all_users[username]
            LIST_FILE.write_text(json.dumps(all_users, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        return {"error": "Erro ao atualizar lista de usuários."}, 500

    return {"message": f"Usuário '{username}' excluído com sucesso."}, 200


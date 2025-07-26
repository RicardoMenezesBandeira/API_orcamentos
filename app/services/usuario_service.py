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
# Helpers
# ---------------------------------------------------------------------------

def _is_admin(user_data: dict) -> bool:
    return user_data.get("admin", False)

# ---------------------------------------------------------------------------
# A) cadastrar_usuario  (POST /add_usuario)
# ---------------------------------------------------------------------------






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


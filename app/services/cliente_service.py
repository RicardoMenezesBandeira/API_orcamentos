from __future__ import annotations

"""Camada de serviço para operações de cliente: cadastro, listagem, deleção.
Mantém nomes originais para facilitar a transição: cadastra_cliente, get_cliente, delete_cliente.
Cada função devolve tuplas (dict, status_code) prontos para jsonify/response.
"""

from pathlib import Path
import json
import os

BD_CLIENTES = Path('bd/clientes')
BD_CLIENTES.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. cadastra_cliente  (POST)
# ---------------------------------------------------------------------------

def cadastra_cliente(cliente: dict):
    """Salva JSON {cliente} como bd/clientes/{cnpj}.json."""
    cnpj = str(cliente.get('cnpj', '')).strip()
    if not cnpj:
        return {"message": "CNPJ não fornecido!"}, 400

    path = BD_CLIENTES / f"{cnpj}.json"
    try:
        with path.open('w', encoding='utf-8') as f:
            json.dump(cliente, f, indent=2, ensure_ascii=False)
        return {"message": "Cliente cadastrado com sucesso!"}, 200
    except Exception as e:
        return {"message": f"Erro ao salvar cliente: {e}"}, 500

# ---------------------------------------------------------------------------
# 2. get_cliente (GET) – lista todos
# ---------------------------------------------------------------------------

def get_cliente():
    """Retorna lista de todos os JSONs em bd/clientes."""
    clientes = []
    for arq in BD_CLIENTES.glob('*.json'):
        try:
            with arq.open('r', encoding='utf-8') as f:
                dados = json.load(f)
                clientes.append(dados)
        except json.JSONDecodeError:
            continue  # ignora arquivos corrompidos
    return clientes, 200

# ---------------------------------------------------------------------------
# 3. delete_cliente (DELETE)
# ---------------------------------------------------------------------------

def delete_cliente(cnpj: str):
    """Remove bd/clientes/{cnpj}.json se existir."""
    arq = BD_CLIENTES / f"{cnpj}.json"
    if not arq.exists():
        return {"message": "Arquivo de clientes não encontrado"}, 404
    try:
        arq.unlink()
        return {"message": "Cliente deletado com sucesso"}, 200
    except Exception as e:
        return {"message": f"Erro ao deletar cliente: {e}"}, 500

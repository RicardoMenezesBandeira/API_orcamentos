from flask import Blueprint, request, jsonify, render_template

from ..decorators.auth import token_required
from ..services import cliente_service as svc

bp = Blueprint("cliente", __name__)

# ---------------------------------------------------------------------------
# Rotas de Cliente – mantêm endpoints equivalentes aos do api.py/cadastra.py
# ---------------------------------------------------------------------------

@bp.route("/p_cadastro_cliente", methods=["GET"])
@token_required
def page_cadastro_cliente(user_data):
    """Exibe a página de cadastro de cliente."""
    return render_template("cadastro_cliente.html")


@bp.route("/cadastra_cliente", methods=["POST"])
@token_required
def cadastra_cliente(user_data):
    """Cadastra um novo cliente. Recebe JSON no corpo."""
    dados = request.get_json(force=True)
    payload, status = svc.cadastra_cliente(dados)
    return jsonify(payload), status


@bp.route("/get_cliente", methods=["GET"])
@token_required
def get_cliente(user_data):
    """Retorna lista de clientes."""
    clientes, status = svc.get_cliente()
    return jsonify(clientes), status


@bp.route("/delete_cliente/<cnpj>", methods=["DELETE"])
@token_required
def delete_cliente(user_data, cnpj: str):
    """Deleta o JSON do cliente informado pelo CNPJ."""
    payload, status = svc.delete_cliente(cnpj)
    return jsonify(payload), status

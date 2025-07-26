from flask import Blueprint, request, jsonify, render_template

from ..decorators.auth import token_required
from ..services import usuario_service as svc
from cadastra import cadastrar
from ..utils.helpers import get_data
bp = Blueprint("usuario", __name__)

# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------

@bp.route("/cadastro")
@token_required
def cadastro_page(user_data):
    return render_template("cadastro_usuario.html")

# ---------------------------------------------------------------------------
# Ações CRUD
# ---------------------------------------------------------------------------
@bp.route("/add_usuario", methods=["POST"])
@token_required
def cadastrar_usuario(user_data):
    """
    Recebe JSON com dados de usuário e chama a função cadastrar().
    """
    dados = get_data(user_data.get("nome"))
    permision = dados.get("admin")
    if not permision:
        return jsonify({"message": "Acesso não autorizado!"}), 401 # Não mudar esta mensagem, pois o front-end depende dela.
    data = request.get_json(force=True)
    success = cadastrar(data)
    if success:
        return jsonify({"message": "Usuário adicionado com sucesso!"}), 200
    else:
        return jsonify({"message": "Erro ao adicionar usuário!"}), 500


@bp.route("/usuario", methods=["GET"])
@token_required
def usuario_list(user_data):
    usuarios, status = svc.get_usuario()
    return jsonify(usuarios), status


@bp.route("/delete_usuario/<username>", methods=["DELETE"])
@token_required
def delete_usuario(user_data, username):
    payload, status = svc.delete_usuario(username, user_data)
    return jsonify(payload), status

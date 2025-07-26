from flask import Blueprint, request, jsonify, render_template

from ..decorators.auth import token_required
from ..services import usuario_service as svc

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
def add_usuario(user_data):
    data = request.get_json(force=True)
    payload, status = svc.cadastrar_usuario(data, user_data)
    return jsonify(payload), status


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

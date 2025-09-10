from flask import Blueprint, request, jsonify, render_template, make_response, current_app

from ..decorators.auth import token_required, logon, logout  # mesmas funções do login.py original

bp = Blueprint("auth", __name__)

# ---------------------------------------------------------------------------
# Rotas de autenticação – mantêm nomes e comportamento do api.py
# ---------------------------------------------------------------------------

@bp.route("/")
def login_page():
    """Exibe a página de login (GET raiz)."""
    return render_template("login.html")


@bp.route("/login", methods=["POST"])
def login():
    """Autentica usuário, devolve JWT em cookie + JSON de confirmação."""
    data = request.get_json(force=True)
    usuario = data.get("username")
    senha   = data.get("password")

    res = logon(usuario, senha, current_app.config["SECRET_KEY"])
    if res["token"] == "erro":
        return jsonify({"message": "Usuário ou senha inválidos!"}), 401

    resp = make_response(jsonify({"message": "Login bem‑sucedido", "user": res["user"]}))
    resp.set_cookie(
        "auth_token", res["token"], httponly=True,
        secure=False,  # troque para True se usar HTTPS em produção
        samesite="Lax"
    )
    print(resp)
    return resp


@bp.route("/logout", methods=["GET"])
@token_required
def logout_route(user_data):
    """Remove token da memória e do cookie."""
    logout()
    resp = make_response(jsonify({"message": "Logout bem‑sucedido"}))
    resp.set_cookie("auth_token", "", expires=0)  # limpa cookie
    return resp

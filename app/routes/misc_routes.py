from flask import Blueprint, render_template, send_from_directory
from ..decorators.auth import token_required
from ..utils.helpers import get_data

bp = Blueprint("misc", __name__)

@bp.route("/dashboard", methods=['GET'])
@token_required
def get_dashboard(user_data):

    user     = user_data.get("user")
    dados =   get_data(user)
    nome = dados.get("nome")
    info     = f"Nome: {nome}"
    btn = "<input type='text' class='search' placeholder='Buscar Nº de orçamento...' oninput='filtrarOrcamentos(this.value)'><button class='btn' onclick='novoOrcamento()'>gerar novo orçamento</button>"
    if dados.get("admin"):
        btn += " <button class='btn' onclick='novoFuncionario()'>cadastra empregado</button>"

    return render_template('index.html', info=info, btns=btn), 200
@bp.route("/template-PDF/<path:filename>")
def serve_template(filename):
    return send_from_directory("template-PDF", filename)

@bp.route("/dev_god")
def dev_god():
    return "Bernardo Ribeiro , Caio Ferreira , Ricardo Bandeira", 200

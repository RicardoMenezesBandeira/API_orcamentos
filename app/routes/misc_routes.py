from flask import Blueprint, render_template, send_from_directory
from ..decorators.auth import token_required
from ..utils.helpers import get_data

bp = Blueprint("misc", __name__)

@bp.route("/dashboard", methods=['GET'])
@token_required
def dashboard(user_data):
    return render_template("index.html")

@bp.route("/template-PDF/<path:filename>")
def serve_template(filename):
    return send_from_directory("template-PDF", filename)

@bp.route("/dev_god")
def dev_god():
    return "Bernardo Ribeiro , Caio Ferreira , Ricardo Bandeira", 200

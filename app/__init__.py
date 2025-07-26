"""
app/__init__.py  ─  fábrica do Flask

• Registra todos os blueprints:
    - auth_routes
    - orcamento_routes
    - cliente_routes
    - usuario_routes
    - misc_routes
• Habilita CORS
• Adiciona o diretório template-PDF ao loader do Jinja2
"""

from flask import Flask
from flask_cors import CORS
from jinja2 import ChoiceLoader, FileSystemLoader


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    # ------------------------------------------------------------------
    # Configurações básicas
    # ------------------------------------------------------------------
    app.config["SECRET_KEY"] = "meusegredosecreto"

    # CORS global (usa cookies)
    CORS(app, supports_credentials=True)

    # Loader extra para que o Jinja encontre também template-PDF/*
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader("../template-PDF"),
        app.jinja_loader,
    ])

    # ------------------------------------------------------------------
    # Registro dos Blueprints
    # ------------------------------------------------------------------
    from .routes import (
        auth_routes,
        orcamento_routes,
        cliente_routes,
        usuario_routes,
        misc_routes,
    )

    for bp in (
        auth_routes.bp,
        orcamento_routes.bp,
        cliente_routes.bp,
        usuario_routes.bp,
        misc_routes.bp,
    ):
        app.register_blueprint(bp)

    # ------------------------------------------------------------------
    # Cabeçalhos CORS extra para todas as respostas
    # ------------------------------------------------------------------
    @app.after_request
    def add_cors_headers(resp):
        resp.headers.setdefault(
            "Access-Control-Allow-Headers",
            "Content-Type,Authorization,x-access-token"
        )
        resp.headers.setdefault(
            "Access-Control-Allow-Methods",
            "GET,POST,PUT,DELETE,OPTIONS"
        )
        return resp

    return app

"""SIAGAPIM — Flask application factory."""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from app.config import Config
from app.extensions import db


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    from app.api import register_blueprints

    register_blueprints(app)

    with app.app_context():
        try:
            from app.utils.project_scope import ensure_issue_project_id_column

            ensure_issue_project_id_column()
        except Exception:
            pass

    @app.get("/api/health")
    def health():
        return {
            "status": "ok",
            "service": "siagapim",
            "name": "SIAGAPIM BANTEN",
            "full_name": "Sistem Informasi Analisis Gema Aktual Pimpinan",
        }

    return app

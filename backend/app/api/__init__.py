"""API blueprint registration."""

from flask import Flask


def register_blueprints(app: Flask) -> None:
    from app.api.agenda import bp as agenda_bp
    from app.api.alerts import bp as alerts_bp
    from app.api.archive import bp as archive_bp
    from app.api.auth import bp as auth_bp
    from app.api.content import bp as content_bp
    from app.api.dashboard import bp as dashboard_bp
    from app.api.executive import bp as executive_bp
    from app.api.issues import bp as issues_bp
    from app.api.kol import bp as kol_bp
    from app.api.mata_bathin import bp as mata_bathin_bp
    from app.api.media import bp as media_bp
    from app.api.missions import bp as missions_bp
    from app.api.opds import bp as opds_bp
    from app.api.reports import bp as reports_bp
    from app.api.settings import bp as settings_bp
    from app.api.users import bp as users_bp
    from app.api.validations import bp as validations_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(issues_bp, url_prefix="/api/issues")
    app.register_blueprint(mata_bathin_bp, url_prefix="/api/mata-bathin")
    app.register_blueprint(validations_bp, url_prefix="/api/validations")
    app.register_blueprint(content_bp, url_prefix="/api/content")
    app.register_blueprint(media_bp, url_prefix="/api/media")
    app.register_blueprint(missions_bp, url_prefix="/api/missions")
    app.register_blueprint(kol_bp, url_prefix="/api/kol")
    app.register_blueprint(executive_bp, url_prefix="/api/executive")
    app.register_blueprint(alerts_bp, url_prefix="/api/alerts")
    app.register_blueprint(archive_bp, url_prefix="/api/archive")
    app.register_blueprint(agenda_bp, url_prefix="/api/agenda")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(settings_bp, url_prefix="/api/settings")
    app.register_blueprint(opds_bp, url_prefix="/api/opds")

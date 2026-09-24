"""Application settings API (news source, etc.)."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.services.app_settings import messaging_public, news_source_public, save_messaging, set_news_source
from app.utils.auth import role_required

bp = Blueprint("settings", __name__)


@bp.get("/news-source")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan", "media_kol_admin", "opd_admin", "asn")
def get_news_source_setting():
    return jsonify({"data": news_source_public()})


@bp.put("/news-source")
@jwt_required()
@role_required("super_admin", "editor")
def put_news_source_setting():
    body = request.get_json(silent=True) or {}
    source = body.get("news_source") or body.get("source") or ""
    try:
        set_news_source(str(source))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"data": news_source_public()})


@bp.get("/messaging")
@jwt_required()
@role_required("super_admin", "editor")
def get_messaging_setting():
    return jsonify({"data": messaging_public()})


@bp.put("/messaging")
@jwt_required()
@role_required("super_admin", "editor")
def put_messaging_setting():
    body = request.get_json(silent=True) or {}
    try:
        data = save_messaging(body)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"data": data})

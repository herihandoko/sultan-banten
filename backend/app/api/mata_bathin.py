"""Mata Bathin integration endpoints (webhook ingest + status)."""

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from app.services.mata_bathin import MataBathinClient, ingest_crisis_alert
from app.utils.auth import role_required

bp = Blueprint("mata_bathin", __name__)


@bp.get("/status")
@jwt_required()
@role_required("super_admin", "editor")
def integration_status():
    client = MataBathinClient()
    return jsonify(
        {
            "enabled": current_app.config["MATA_BATHIN_ENABLED"],
            "base_url": current_app.config["MATA_BATHIN_BASE_URL"] or None,
            "reachable": client.health_check() if current_app.config["MATA_BATHIN_ENABLED"] else False,
        }
    )


@bp.post("/webhook/alert")
def receive_alert():
    """
    Ingest crisis alert from Mata Bathin.
    Auth via API key header when configured; open in local demo if key empty.
    """
    expected = current_app.config.get("MATA_BATHIN_API_KEY") or ""
    if expected:
        provided = request.headers.get("X-API-Key", "")
        if provided != expected:
            return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    if not payload.get("alert_id") and not payload.get("title"):
        return jsonify({"error": "Payload alert tidak valid"}), 400

    issue, created = ingest_crisis_alert(payload)
    return jsonify({"data": issue.to_dict(include_relations=True), "created": created}), (
        201 if created else 200
    )

"""PRD §9.1 — export laporan PDF/Excel."""

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required
from io import BytesIO

from app.services import reports as report_svc
from app.utils.auth import get_current_user, role_required

bp = Blueprint("reports", __name__)

EXPORT_ROLES = ("super_admin", "editor", "pimpinan", "media_kol_admin")


@bp.get("/types")
@jwt_required()
@role_required(*EXPORT_ROLES)
def list_types():
    return jsonify(
        {
            "data": [
                {
                    "code": "crisis",
                    "name": "Laporan Penanganan Krisis",
                    "formats": ["pdf", "xlsx"],
                },
                {
                    "code": "media_sla",
                    "name": "Laporan Aktivitas Media (SLA)",
                    "formats": ["pdf", "xlsx"],
                },
                {
                    "code": "asn",
                    "name": "Rekap Partisipasi ASN per OPD",
                    "formats": ["pdf", "xlsx"],
                },
                {
                    "code": "kol",
                    "name": "Laporan Kinerja KOL & Campaign",
                    "formats": ["pdf", "xlsx"],
                },
                {
                    "code": "executive",
                    "name": "Executive Brief",
                    "formats": ["pdf", "xlsx"],
                },
            ]
        }
    )


@bp.get("/export/<report_code>")
@jwt_required()
@role_required(*EXPORT_ROLES)
def export_report(report_code: str):
    fmt = (request.args.get("format") or "pdf").lower()
    if fmt not in {"pdf", "xlsx"}:
        return jsonify({"error": "format harus pdf atau xlsx"}), 400

    # Role scoping: media_kol_admin only media_sla + kol
    user = get_current_user()
    role = user.role.code if user and user.role else None
    if role == "media_kol_admin" and report_code not in {"media_sla", "kol"}:
        return jsonify({"error": "Forbidden"}), 403
    if role == "editor" and report_code == "executive":
        # editor may still export ops reports
        pass

    user_id = user.id if user else None
    issue_id = request.args.get("issue_id", type=int)
    project_id = (request.args.get("project_id") or request.args.get("keyword_id") or "").strip() or None

    try:
        if report_code == "crisis":
            content, mime, filename = report_svc.export_crisis(
                fmt, issue_id, user_id, project_id=project_id
            )
        elif report_code == "media_sla":
            content, mime, filename = report_svc.export_media_sla(fmt, user_id)
        elif report_code == "asn":
            content, mime, filename = report_svc.export_asn(fmt, user_id)
        elif report_code == "kol":
            content, mime, filename = report_svc.export_kol(fmt, user_id)
        elif report_code == "executive":
            content, mime, filename = report_svc.export_executive(
                fmt, user_id, project_id=project_id
            )
        else:
            return jsonify({"error": "Jenis laporan tidak dikenal"}), 404
    except Exception as exc:  # noqa: BLE001 — surface export errors cleanly
        return jsonify({"error": f"Gagal membuat laporan: {exc}"}), 500

    return send_file(
        BytesIO(content),
        mimetype=mime,
        as_attachment=True,
        download_name=filename,
    )

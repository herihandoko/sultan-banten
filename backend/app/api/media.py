"""F.06 Media Partners + F.07 SLA Tracker + F.08 One-Click Media Blast."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import (
    AuditLog,
    ContentItem,
    Issue,
    MediaBlastLog,
    MediaPartner,
    MediaSlaLog,
)
from app.services.messaging import (
    deliver_to_partner,
    messaging_status,
    send_email,
    send_whatsapp,
)
from app.utils.auth import get_current_user, role_required
from app.utils.pagination import paginate
from app.utils.project_scope import filter_query_by_issue_ids, issue_ids_for_project, request_project_id

bp = Blueprint("media", __name__)

SLA_MINUTES = 60  # PRD: SLA 1 jam


@bp.get("/messaging-status")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin", "pimpinan")
def get_messaging_status():
    """Status gateway WA/email (tanpa secret) untuk UI Media Hub."""
    return jsonify({"data": messaging_status()})


@bp.post("/test-email")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin")
def test_email():
    """Uji kirim email SMTP (satu penerima)."""
    data = request.get_json(silent=True) or {}
    to = (data.get("to") or "").strip()
    if not to:
        return jsonify({"error": "to (alamat email) wajib"}), 400
    subject = (data.get("subject") or "[SIAGAPIM] Test email").strip()
    body = (
        data.get("body")
        or "Ini adalah email uji dari SIAGAPIM Media Hub.\n\nJika Anda menerima pesan ini, konfigurasi SMTP sudah benar."
    )
    result = send_email(to, subject, body)
    user = get_current_user()
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="test_email",
            entity_type="messaging",
            entity_id=None,
            details={"to": to, "status": result.get("status"), "error": result.get("error")},
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    code = 200 if result.get("status") == "sent" else 502
    return jsonify({"data": result}), code


@bp.post("/test-whatsapp")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin")
def test_whatsapp():
    """Uji kirim WhatsApp via Fonnte (satu nomor)."""
    data = request.get_json(silent=True) or {}
    to = (data.get("to") or "").strip()
    if not to:
        return jsonify({"error": "to (nomor WhatsApp) wajib"}), 400
    message = (
        data.get("message")
        or "Ini adalah pesan uji dari SIAGAPIM Media Hub via Fonnte."
    )
    result = send_whatsapp(to, message)
    user = get_current_user()
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="test_whatsapp",
            entity_type="messaging",
            entity_id=None,
            details={"to": to, "status": result.get("status"), "error": result.get("error")},
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    code = 200 if result.get("status") == "sent" else 502
    return jsonify({"data": result}), code


# ── F.06 Database Media Mitra ───────────────────────────────────────────────


@bp.get("/partners")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin", "pimpinan")
def list_partners():
    active = request.args.get("active")  # 1 | 0 | omit
    q = (request.args.get("q") or "").strip()
    query = MediaPartner.query
    if active == "1":
        query = query.filter_by(is_active=True)
    elif active == "0":
        query = query.filter_by(is_active=False)
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                MediaPartner.name.ilike(like),
                MediaPartner.editor_name.ilike(like),
                MediaPartner.coverage_area.ilike(like),
                MediaPartner.email.ilike(like),
            )
        )
    query = query.order_by(MediaPartner.name)
    return jsonify(paginate(query, lambda p: p.to_dict(), default_per_page=10, max_per_page=200))


@bp.post("/partners")
@jwt_required()
@role_required("super_admin", "media_kol_admin", "editor")
def create_partner():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Nama media wajib diisi"}), 400

    partner = MediaPartner(
        name=name,
        editor_name=data.get("editor_name"),
        whatsapp=data.get("whatsapp"),
        email=data.get("email"),
        coverage_area=data.get("coverage_area"),
        crisis_channel=data.get("crisis_channel"),
        notes=data.get("notes"),
        is_active=bool(data.get("is_active", True)),
    )
    db.session.add(partner)
    user = get_current_user()
    db.session.flush()
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="create_media_partner",
            entity_type="media_partner",
            entity_id=partner.id,
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"data": partner.to_dict()}), 201


@bp.patch("/partners/<int:partner_id>")
@jwt_required()
@role_required("super_admin", "media_kol_admin", "editor")
def update_partner(partner_id: int):
    partner = MediaPartner.query.get_or_404(partner_id)
    data = request.get_json(silent=True) or {}
    for field in (
        "name",
        "editor_name",
        "whatsapp",
        "email",
        "coverage_area",
        "crisis_channel",
        "notes",
    ):
        if field in data:
            value = data[field]
            if field == "name":
                value = (value or "").strip()
                if not value:
                    return jsonify({"error": "Nama media tidak boleh kosong"}), 400
            setattr(partner, field, value)
    if "is_active" in data:
        partner.is_active = bool(data["is_active"])

    user = get_current_user()
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="update_media_partner",
            entity_type="media_partner",
            entity_id=partner.id,
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"data": partner.to_dict()})


@bp.delete("/partners/<int:partner_id>")
@jwt_required()
@role_required("super_admin", "media_kol_admin")
def deactivate_partner(partner_id: int):
    partner = MediaPartner.query.get_or_404(partner_id)
    partner.is_active = False
    db.session.commit()
    return jsonify({"data": partner.to_dict()})


# ── F.08 One-Click Media Blast ──────────────────────────────────────────────


@bp.get("/blasts")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin", "pimpinan")
def list_blasts():
    status = request.args.get("status")
    q = (request.args.get("q") or "").strip()
    query = MediaBlastLog.query
    query = filter_query_by_issue_ids(query, MediaBlastLog.issue_id, request_project_id())
    if status:
        query = query.filter_by(status=status)
    if q:
        like = f"%{q}%"
        query = query.outerjoin(ContentItem, MediaBlastLog.content_id == ContentItem.id).filter(
            db.or_(
                MediaBlastLog.channel.ilike(like),
                ContentItem.title.ilike(like),
            )
        )
    query = query.order_by(MediaBlastLog.sent_at.desc())
    return jsonify(paginate(query, lambda b: b.to_dict()))


@bp.get("/blasts/<int:blast_id>")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin", "pimpinan")
def get_blast(blast_id: int):
    log = MediaBlastLog.query.get_or_404(blast_id)
    return jsonify({"data": log.to_dict()})


@bp.get("/blast-ready-content")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin")
def blast_ready_content():
    """Konten approved yang siap di-blast."""
    items_q = ContentItem.query.filter(ContentItem.status.in_(["approved", "published"]))
    items_q = filter_query_by_issue_ids(items_q, ContentItem.issue_id, request_project_id())
    items = items_q.order_by(ContentItem.updated_at.desc()).all()
    return jsonify(
        {
            "data": [
                {
                    "id": i.id,
                    "title": i.title,
                    "content_type": i.content_type,
                    "body": i.body,
                    "media_url": i.media_url,
                    "status": i.status,
                    "issue_id": i.issue_id,
                    "issue_title": i.issue.title if i.issue else None,
                }
                for i in items
            ]
        }
    )


@bp.post("/blast")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin")
def one_click_blast():
    """
    One-click media blast: kirim konten ke semua (atau subset) media mitra aktif
    via WhatsApp (Fonnte) / Email (SMTP).
    """
    data = request.get_json(silent=True) or {}
    content_id = data.get("content_id")
    channel = data.get("channel", "both")
    partner_ids = data.get("partner_ids")  # optional subset

    if channel not in {"whatsapp", "email", "both"}:
        return jsonify({"error": "channel harus whatsapp, email, atau both"}), 400
    if not content_id:
        return jsonify({"error": "content_id wajib"}), 400

    content = ContentItem.query.get(content_id)
    if not content:
        return jsonify({"error": "Konten tidak ditemukan"}), 404
    if content.status not in {"approved", "published"}:
        return jsonify({"error": "Hanya konten approved/published yang bisa di-blast"}), 400

    query = MediaPartner.query.filter_by(is_active=True)
    if partner_ids:
        query = query.filter(MediaPartner.id.in_(partner_ids))
    partners = query.order_by(MediaPartner.name).all()
    if not partners:
        return jsonify({"error": "Tidak ada media mitra aktif"}), 400

    subject = f"[SIAGAPIM] {content.title}"
    body = content.body or content.title
    if content.media_url:
        body = f"{body}\n\nLampiran: {content.media_url}"

    recipients = []
    delivery_results = []
    sent_count = 0
    fail_count = 0

    for partner in partners:
        partner_payload = partner.to_dict()
        recipients.append(
            {
                "id": partner.id,
                "name": partner.name,
                "whatsapp": partner.whatsapp,
                "email": partner.email,
            }
        )
        results = deliver_to_partner(partner_payload, channel, subject, body)
        for r in results:
            r["partner_id"] = partner.id
            r["partner_name"] = partner.name
            delivery_results.append(r)
            if r["status"] == "sent":
                sent_count += 1
            else:
                fail_count += 1

    if fail_count == 0:
        status = "sent"
    elif sent_count == 0:
        status = "failed"
    else:
        status = "partial"

    user = get_current_user()
    log = MediaBlastLog(
        issue_id=content.issue_id,
        content_id=content.id,
        sent_by=user.id if user else None,
        channel=channel,
        recipients=recipients,
        status=status,
        result={
            "sent": sent_count,
            "failed": fail_count,
            "deliveries": delivery_results,
        },
    )
    db.session.add(log)

    if status in {"sent", "partial"}:
        content.status = "published"
        issue = content.issue or Issue.query.get(content.issue_id)
        if issue and issue.status in {"approved", "producing"}:
            issue.status = "disseminated"

    db.session.flush()
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="media_blast",
            entity_type="media_blast_log",
            entity_id=log.id,
            details={
                "content_id": content.id,
                "channel": channel,
                "partners": len(partners),
                "status": status,
            },
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()

    feedback_result = None
    if status in {"sent", "partial"} and content.issue_id:
        issue = Issue.query.get(content.issue_id)
        if issue:
            from app.services.feedback import push_issue_feedback

            feedback_result = push_issue_feedback(
                issue, notes="Feedback setelah media blast"
            )

    data = log.to_dict()
    if feedback_result is not None:
        data["mata_bathin_feedback"] = {
            "sent": feedback_result.get("sent"),
            "reason": feedback_result.get("reason"),
        }
    return jsonify({"data": data}), 201


# ── F.07 SLA Compliance Tracker ─────────────────────────────────────────────


def _parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _sla_payload(item: MediaSlaLog) -> dict:
    data = item.to_dict()
    partner = MediaPartner.query.get(item.media_partner_id)
    if partner:
        data["partner_name"] = partner.name
    if item.blast_log_id:
        blast = MediaBlastLog.query.get(item.blast_log_id)
        if blast:
            data["blast_sent_at"] = blast.sent_at.isoformat() if blast.sent_at else None
            data["content_id"] = blast.content_id
    return data


@bp.get("/sla")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin", "pimpinan")
def list_sla_logs():
    query = MediaSlaLog.query
    project_id = request_project_id()
    ids = issue_ids_for_project(project_id)
    if ids is not None:
        query = query.join(MediaBlastLog, MediaSlaLog.blast_log_id == MediaBlastLog.id).filter(
            MediaBlastLog.issue_id.in_(ids or [-1])
        )
    query = query.order_by(MediaSlaLog.created_at.desc())
    result = paginate(query, _sla_payload)
    result["sla_minutes"] = SLA_MINUTES
    return jsonify(result)


@bp.get("/sla/ranking")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin", "pimpinan")
def sla_ranking():
    partners = MediaPartner.query.filter_by(is_active=True).order_by(MediaPartner.name).all()
    ranking = []
    for partner in partners:
        logs = MediaSlaLog.query.filter_by(media_partner_id=partner.id).all()
        total = len(logs)
        compliant = sum(1 for x in logs if x.sla_compliant)
        avg_minutes = (
            round(sum(x.response_minutes or 0 for x in logs) / total, 1) if total else None
        )
        rate = round((compliant / total) * 100, 1) if total else None
        ranking.append(
            {
                "partner_id": partner.id,
                "partner_name": partner.name,
                "total_logs": total,
                "compliant": compliant,
                "compliance_rate": rate,
                "avg_response_minutes": avg_minutes,
            }
        )
    ranking.sort(
        key=lambda x: (
            x["compliance_rate"] is not None,
            x["compliance_rate"] or -1,
            -(x["avg_response_minutes"] or 9999),
        ),
        reverse=True,
    )
    return jsonify({"data": ranking, "sla_minutes": SLA_MINUTES})


@bp.post("/sla")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin")
def create_sla_log():
    """Catat waktu tayang & kepatuhan SLA media mitra (target 1 jam)."""
    data = request.get_json(silent=True) or {}
    partner_id = data.get("media_partner_id")
    if not partner_id or not MediaPartner.query.get(partner_id):
        return jsonify({"error": "media_partner_id tidak valid"}), 400

    blast_log_id = data.get("blast_log_id")
    blast = None
    if blast_log_id:
        blast = MediaBlastLog.query.get(blast_log_id)
        if not blast:
            return jsonify({"error": "blast_log_id tidak ditemukan"}), 404

    published_at = _parse_dt(data.get("published_at")) or datetime.now(timezone.utc)

    response_minutes = data.get("response_minutes")
    if response_minutes is None and blast and blast.sent_at:
        sent = blast.sent_at
        if sent.tzinfo is None:
            sent = sent.replace(tzinfo=timezone.utc)
        pub = published_at if published_at.tzinfo else published_at.replace(tzinfo=timezone.utc)
        delta = pub - sent
        response_minutes = max(0, int(delta.total_seconds() // 60))
    elif response_minutes is not None:
        response_minutes = int(response_minutes)

    content_match = data.get("content_match")
    if content_match is None:
        content_match = True
    else:
        content_match = bool(content_match)

    sla_compliant = data.get("sla_compliant")
    if sla_compliant is None:
        sla_compliant = (
            response_minutes is not None
            and response_minutes <= SLA_MINUTES
            and content_match
        )
    else:
        sla_compliant = bool(sla_compliant)

    item = MediaSlaLog(
        media_partner_id=partner_id,
        blast_log_id=blast_log_id,
        published_at=published_at,
        response_minutes=response_minutes,
        content_match=content_match,
        sla_compliant=sla_compliant,
        notes=data.get("notes"),
    )
    db.session.add(item)
    user = get_current_user()
    db.session.flush()
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="create_sla_log",
            entity_type="media_sla_log",
            entity_id=item.id,
            details={"compliant": sla_compliant, "response_minutes": response_minutes},
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"data": _sla_payload(item)}), 201

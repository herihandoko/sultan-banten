"""F.12 Direktori KOL + F.13 KOL Campaign Tracker."""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import AuditLog, Issue, KolCampaign, KolPartner
from app.utils.auth import get_current_user, role_required
from app.utils.pagination import paginate
from app.utils.project_scope import filter_query_by_issue_ids, request_project_id

bp = Blueprint("kol", __name__)

CONTRACT_STATUSES = {"prospect", "active", "expired", "terminated"}
CAMPAIGN_STATUSES = {"planned", "in_progress", "published", "completed", "cancelled"}
BUDGET_STATUSES = {"planned", "approved", "paid", "cancelled"}
PLATFORMS = {"instagram", "tiktok", "youtube", "twitter", "facebook", "other"}


def _parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _campaign_payload(campaign: KolCampaign) -> dict:
    data = campaign.to_dict()
    if campaign.kol:
        data["kol"] = {
            "id": campaign.kol.id,
            "name": campaign.kol.name,
            "platform": campaign.kol.platform,
            "handle": campaign.kol.handle,
        }
    if campaign.issue_id:
        issue = Issue.query.get(campaign.issue_id)
        if issue:
            data["issue_title"] = issue.title
    return data


# ── F.12 Direktori KOL ──────────────────────────────────────────────────────


@bp.get("/partners")
@jwt_required()
@role_required("super_admin", "media_kol_admin", "editor", "pimpinan")
def list_partners():
    active = request.args.get("active")  # 1 | 0 | omit
    platform = request.args.get("platform")
    contract_status = request.args.get("contract_status")
    q = (request.args.get("q") or "").strip()
    query = KolPartner.query
    if active == "1":
        query = query.filter_by(is_active=True)
    elif active == "0":
        query = query.filter_by(is_active=False)
    if platform:
        query = query.filter_by(platform=platform)
    if contract_status:
        query = query.filter_by(contract_status=contract_status)
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                KolPartner.name.ilike(like),
                KolPartner.handle.ilike(like),
                KolPartner.topics.ilike(like),
            )
        )
    query = query.order_by(KolPartner.name)
    return jsonify(
        paginate(
            query,
            lambda p: {**p.to_dict(), "campaign_count": len(p.campaigns)},
            max_per_page=200,
        )
    )


@bp.post("/partners")
@jwt_required()
@role_required("super_admin", "media_kol_admin")
def create_partner():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Nama KOL wajib diisi"}), 400

    platform = data.get("platform") or "instagram"
    if platform not in PLATFORMS:
        return jsonify({"error": f"platform: {', '.join(sorted(PLATFORMS))}"}), 400

    contract_status = data.get("contract_status") or "prospect"
    if contract_status not in CONTRACT_STATUSES:
        return jsonify({"error": "contract_status tidak valid"}), 400

    partner = KolPartner(
        name=name,
        platform=platform,
        handle=data.get("handle"),
        followers=int(data.get("followers") or 0),
        engagement_rate=float(data.get("engagement_rate") or 0),
        topics=data.get("topics"),
        contract_status=contract_status,
        notes=data.get("notes"),
        is_active=bool(data.get("is_active", True)),
    )
    db.session.add(partner)
    user = get_current_user()
    db.session.flush()
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="create_kol",
            entity_type="kol_partner",
            entity_id=partner.id,
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"data": partner.to_dict()}), 201


@bp.patch("/partners/<int:partner_id>")
@jwt_required()
@role_required("super_admin", "media_kol_admin")
def update_partner(partner_id: int):
    partner = KolPartner.query.get_or_404(partner_id)
    data = request.get_json(silent=True) or {}

    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"error": "Nama tidak boleh kosong"}), 400
        partner.name = name
    if "platform" in data:
        if data["platform"] not in PLATFORMS:
            return jsonify({"error": "platform tidak valid"}), 400
        partner.platform = data["platform"]
    if "handle" in data:
        partner.handle = data["handle"]
    if "followers" in data:
        partner.followers = int(data["followers"] or 0)
    if "engagement_rate" in data:
        partner.engagement_rate = float(data["engagement_rate"] or 0)
    if "topics" in data:
        partner.topics = data["topics"]
    if "contract_status" in data:
        if data["contract_status"] not in CONTRACT_STATUSES:
            return jsonify({"error": "contract_status tidak valid"}), 400
        partner.contract_status = data["contract_status"]
    if "notes" in data:
        partner.notes = data["notes"]
    if "is_active" in data:
        partner.is_active = bool(data["is_active"])

    db.session.commit()
    return jsonify({"data": partner.to_dict()})


# ── F.13 KOL Campaign Tracker ───────────────────────────────────────────────


@bp.get("/campaigns")
@jwt_required()
@role_required("super_admin", "media_kol_admin", "editor", "pimpinan")
def list_campaigns():
    status = request.args.get("status")
    budget_status = request.args.get("budget_status")
    q = (request.args.get("q") or "").strip()
    query = KolCampaign.query
    query = filter_query_by_issue_ids(query, KolCampaign.issue_id, request_project_id())
    if status:
        query = query.filter_by(status=status)
    if budget_status:
        query = query.filter_by(budget_status=budget_status)
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                KolCampaign.title.ilike(like),
                KolCampaign.notes.ilike(like),
                KolCampaign.deliverable_url.ilike(like),
            )
        )
    query = query.order_by(KolCampaign.created_at.desc())
    return jsonify(paginate(query, _campaign_payload))


@bp.post("/campaigns")
@jwt_required()
@role_required("super_admin", "media_kol_admin")
def create_campaign():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    kol_id = data.get("kol_id")
    if not title:
        return jsonify({"error": "Judul campaign wajib"}), 400
    if not kol_id or not KolPartner.query.get(kol_id):
        return jsonify({"error": "KOL tidak ditemukan"}), 400

    status = data.get("status") or "planned"
    if status not in CAMPAIGN_STATUSES:
        return jsonify({"error": "status campaign tidak valid"}), 400

    budget_status = data.get("budget_status") or "planned"
    if budget_status not in BUDGET_STATUSES:
        return jsonify({"error": "budget_status tidak valid"}), 400

    budget = None
    if data.get("budget") is not None and data.get("budget") != "":
        try:
            budget = Decimal(str(data["budget"]))
        except (InvalidOperation, ValueError):
            return jsonify({"error": "budget tidak valid"}), 400

    issue_id = data.get("issue_id")
    if issue_id and not Issue.query.get(issue_id):
        return jsonify({"error": "Isu tidak ditemukan"}), 404

    campaign = KolCampaign(
        kol_id=kol_id,
        issue_id=issue_id,
        title=title,
        deliverable_url=data.get("deliverable_url"),
        scheduled_at=_parse_dt(data.get("scheduled_at")),
        published_at=_parse_dt(data.get("published_at")),
        views=int(data.get("views") or 0),
        likes=int(data.get("likes") or 0),
        comments=int(data.get("comments") or 0),
        budget=budget,
        budget_status=budget_status,
        status=status,
        notes=data.get("notes"),
    )
    db.session.add(campaign)
    user = get_current_user()
    db.session.flush()
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="create_kol_campaign",
            entity_type="kol_campaign",
            entity_id=campaign.id,
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"data": _campaign_payload(campaign)}), 201


@bp.patch("/campaigns/<int:campaign_id>")
@jwt_required()
@role_required("super_admin", "media_kol_admin")
def update_campaign(campaign_id: int):
    campaign = KolCampaign.query.get_or_404(campaign_id)
    data = request.get_json(silent=True) or {}

    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "Judul tidak boleh kosong"}), 400
        campaign.title = title
    for field in ("deliverable_url", "notes"):
        if field in data:
            setattr(campaign, field, data[field])
    for field in ("views", "likes", "comments"):
        if field in data:
            setattr(campaign, field, int(data[field] or 0))
    if "scheduled_at" in data:
        campaign.scheduled_at = _parse_dt(data["scheduled_at"])
    if "published_at" in data:
        campaign.published_at = _parse_dt(data["published_at"])
    if "status" in data:
        if data["status"] not in CAMPAIGN_STATUSES:
            return jsonify({"error": "status tidak valid"}), 400
        campaign.status = data["status"]
        if data["status"] == "published" and not campaign.published_at:
            campaign.published_at = datetime.now(timezone.utc)
    if "budget_status" in data:
        if data["budget_status"] not in BUDGET_STATUSES:
            return jsonify({"error": "budget_status tidak valid"}), 400
        campaign.budget_status = data["budget_status"]
    if "budget" in data:
        if data["budget"] is None or data["budget"] == "":
            campaign.budget = None
        else:
            try:
                campaign.budget = Decimal(str(data["budget"]))
            except (InvalidOperation, ValueError):
                return jsonify({"error": "budget tidak valid"}), 400

    db.session.commit()
    return jsonify({"data": _campaign_payload(campaign)})

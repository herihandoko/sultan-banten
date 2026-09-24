"""Crisis Room issue models."""

import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from app.extensions import db

_PRODUCT_NAME = re.compile(r"\s*\b(?:di\s+)?SIPANTAU\b", re.IGNORECASE)


def public_action_text(value) -> str:
    """User-facing action wording, without internal product names."""
    text = _PRODUCT_NAME.sub("", str(value or ""))
    text = re.sub(r"\s{2,}", " ", text).strip(" \t-–—")
    return text


def public_actions(actions):
    if not isinstance(actions, list):
        return actions
    cleaned = []
    for item in actions:
        if not isinstance(item, str):
            if item:
                cleaned.append(item)
            continue
        text = public_action_text(item)
        if text:
            cleaned.append(text)
    return cleaned


def _hostname_label(url: str | None) -> str | None:
    if not url:
        return None
    try:
        host = (urlparse(str(url)).hostname or "").lower()
    except Exception:
        return None
    if not host:
        return None
    if host.startswith("www."):
        host = host[4:]
    # Skip generic aggregators when possible
    if host in {"google.com", "news.google.com", "google.co.id"}:
        return None
    return host


def _pretty_platform(value: str) -> str | None:
    """Map social platforms to display labels. Generic 'news' returns None."""
    raw = (value or "").strip()
    if not raw:
        return None
    key = raw.lower()
    # Too generic for a badge — callers should fall back to hostname/outlet
    if key in {"news", "blog", "media", "media online", "other", "web"}:
        return None
    mapping = {
        "twitter": "X / Twitter",
        "x": "X / Twitter",
        "tiktok": "TikTok",
        "instagram": "Instagram",
        "youtube": "YouTube",
        "facebook": "Facebook",
        "forum": "Forum",
        "reddit": "Reddit",
    }
    return mapping.get(key, raw)


def _display_host(host: str) -> str:
    """Keep hostname readable (bantenraya.co.id, detik.com)."""
    h = (host or "").lower().strip()
    if h.startswith("www."):
        h = h[4:]
    return h


class Issue(db.Model):
    __tablename__ = "issues"

    id = db.Column(db.Integer, primary_key=True)
    mb_alert_id = db.Column(db.String(100), unique=True, index=True)
    title = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text)
    why_now = db.Column(db.Text)
    risk_level = db.Column(db.String(10), default="R0", nullable=False, index=True)
    risk_assessment = db.Column(db.JSON)
    recommended_actions = db.Column(db.JSON)
    status = db.Column(db.String(50), default="open", nullable=False, index=True)
    # open | validating | producing | approved | disseminated | closed
    source = db.Column(db.String(50), default="mata_bathin")  # sipantau | mata_bathin | manual
    # SIPANTAU keyword/project id (e.g. proj-andra-soni) — scopes Crisis Room data
    project_id = db.Column(db.String(100), index=True)
    narrative_card = db.Column(db.JSON)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    closed_at = db.Column(db.DateTime)

    evidence = db.relationship("IssueEvidence", back_populates="issue", cascade="all, delete-orphan")
    validations = db.relationship("OpdValidation", back_populates="issue", cascade="all, delete-orphan")
    content_items = db.relationship("ContentItem", back_populates="issue", cascade="all, delete-orphan")

    def primary_source_label(self) -> str | None:
        """Human outlet/platform for UI (tiktok, detik.com, …) — not sipantau/mata_bathin."""
        skip = {
            "sipantau",
            "mata_bathin",
            "manual",
            "media online",
            "media",
            "news",
            "blog",
            "social",
            "other",
            "web",
        }
        assessment = self.risk_assessment if isinstance(self.risk_assessment, dict) else {}

        # 1) Named outlet from assessment
        for key in ("outlet", "source_name", "author_name", "publisher"):
            val = assessment.get(key)
            if val and str(val).strip().lower() not in skip:
                return str(val).strip()[:80]

        # 2) Evidence URL hostname (detik.com, bantenraya.co.id, …)
        for ev in self.evidence or []:
            host = _hostname_label(ev.url)
            if host:
                return _display_host(host)[:80]
            name = (ev.source_name or "").strip()
            if name and name.lower() not in skip:
                return name[:80]

        # 3) Specific social platform only (tiktok, twitter, …) — never generic "news"
        platform = assessment.get("platform")
        pretty = _pretty_platform(str(platform)) if platform else None
        if pretty and pretty.lower() not in skip:
            return pretty[:80]

        return None

    def primary_source_url(self) -> str | None:
        """First usable evidence / assessment URL for Visit actions."""
        assessment = self.risk_assessment if isinstance(self.risk_assessment, dict) else {}
        for key in ("url", "source_url", "article_url", "evidence_pack_url", "link"):
            val = assessment.get(key)
            if val and str(val).strip().startswith(("http://", "https://")):
                return str(val).strip()[:2000]

        for ev in self.evidence or []:
            url = (ev.url or "").strip()
            if url.startswith(("http://", "https://")):
                return url[:2000]
        return None

    def to_dict(self, include_relations: bool = False):
        data = {
            "id": self.id,
            "mb_alert_id": self.mb_alert_id,
            "title": self.title,
            "summary": self.summary,
            "why_now": self.why_now,
            "risk_level": self.risk_level,
            "risk_assessment": self.risk_assessment,
            "recommended_actions": public_actions(self.recommended_actions),
            "status": self.status,
            "source": self.source,
            "source_label": self.primary_source_label(),
            "source_url": self.primary_source_url(),
            "project_id": self.project_id,
            "narrative_card": self.narrative_card,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }
        if include_relations:
            data["evidence"] = [e.to_dict() for e in self.evidence]
            data["validations"] = [v.to_dict() for v in self.validations]
            data["content_items"] = [c.to_dict() for c in self.content_items]
        return data


class IssueEvidence(db.Model):
    __tablename__ = "issue_evidence"

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey("issues.id"), nullable=False)
    title = db.Column(db.String(255))
    url = db.Column(db.Text)
    source_name = db.Column(db.String(150))
    evidence_type = db.Column(db.String(50))  # article | social | video | other
    snippet = db.Column(db.Text)
    captured_at = db.Column(db.DateTime)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    issue = db.relationship("Issue", back_populates="evidence")

    def to_dict(self):
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "title": self.title,
            "url": self.url,
            "source_name": self.source_name,
            "evidence_type": self.evidence_type,
            "snippet": self.snippet,
            "captured_at": self.captured_at.isoformat() if self.captured_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class OpdValidation(db.Model):
    __tablename__ = "opd_validation"

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey("issues.id"), nullable=False)
    opd_name = db.Column(db.String(150), nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String(50), default="waiting", nullable=False)
    # waiting | validated | rejected
    request_notes = db.Column(db.Text)
    response_notes = db.Column(db.Text)
    response_data = db.Column(db.JSON)
    requested_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    responded_at = db.Column(db.DateTime)

    issue = db.relationship("Issue", back_populates="validations")

    def to_dict(self):
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "opd_name": self.opd_name,
            "requested_by": self.requested_by,
            "assigned_to": self.assigned_to,
            "status": self.status,
            "request_notes": self.request_notes,
            "response_notes": self.response_notes,
            "response_data": self.response_data,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
        }

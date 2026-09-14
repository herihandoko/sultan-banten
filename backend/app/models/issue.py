"""Crisis Room issue models."""

from datetime import datetime, timezone

from app.extensions import db


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

    def to_dict(self, include_relations: bool = False):
        data = {
            "id": self.id,
            "mb_alert_id": self.mb_alert_id,
            "title": self.title,
            "summary": self.summary,
            "why_now": self.why_now,
            "risk_level": self.risk_level,
            "risk_assessment": self.risk_assessment,
            "recommended_actions": self.recommended_actions,
            "status": self.status,
            "source": self.source,
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
    url = db.Column(db.String(500))
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

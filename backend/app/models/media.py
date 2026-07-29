"""Media Hub models."""

from datetime import datetime, timezone

from app.extensions import db


class MediaPartner(db.Model):
    __tablename__ = "media_partners"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    editor_name = db.Column(db.String(150))
    whatsapp = db.Column(db.String(30))
    email = db.Column(db.String(120))
    coverage_area = db.Column(db.String(150))
    crisis_channel = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "editor_name": self.editor_name,
            "whatsapp": self.whatsapp,
            "email": self.email,
            "coverage_area": self.coverage_area,
            "crisis_channel": self.crisis_channel,
            "is_active": self.is_active,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MediaSlaLog(db.Model):
    __tablename__ = "media_sla_logs"

    id = db.Column(db.Integer, primary_key=True)
    media_partner_id = db.Column(db.Integer, db.ForeignKey("media_partners.id"), nullable=False)
    blast_log_id = db.Column(db.Integer, db.ForeignKey("media_blast_logs.id"))
    published_at = db.Column(db.DateTime)
    response_minutes = db.Column(db.Integer)
    content_match = db.Column(db.Boolean)
    sla_compliant = db.Column(db.Boolean)
    notes = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "media_partner_id": self.media_partner_id,
            "blast_log_id": self.blast_log_id,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "response_minutes": self.response_minutes,
            "content_match": self.content_match,
            "sla_compliant": self.sla_compliant,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MediaBlastLog(db.Model):
    __tablename__ = "media_blast_logs"

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey("issues.id"))
    content_id = db.Column(db.Integer, db.ForeignKey("content_items.id"))
    sent_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    channel = db.Column(db.String(50))  # whatsapp | email | both
    recipients = db.Column(db.JSON)
    status = db.Column(db.String(50), default="pending")  # pending | sent | partial | failed
    result = db.Column(db.JSON)
    sent_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "content_id": self.content_id,
            "sent_by": self.sent_by,
            "channel": self.channel,
            "recipients": self.recipients,
            "status": self.status,
            "result": self.result,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
        }

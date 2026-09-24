"""F.02 Crisis alert notifications."""

from datetime import datetime, timezone

from app.extensions import db


class CrisisAlert(db.Model):
    __tablename__ = "crisis_alerts"

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey("issues.id"), index=True)
    alert_type = db.Column(db.String(50), nullable=False)
    # risk_threshold | response_overdue | manual
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    risk_level = db.Column(db.String(10))
    severity = db.Column(db.String(20), default="high")  # info | high | critical
    channels = db.Column(db.JSON)  # ["web", "whatsapp", "telegram"]
    delivery_status = db.Column(db.JSON)  # per-channel mock results
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    read_at = db.Column(db.DateTime)

    issue = db.relationship("Issue", backref=db.backref("crisis_alerts", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "alert_type": self.alert_type,
            "title": self.title,
            "message": self.message,
            "risk_level": self.risk_level,
            "severity": self.severity,
            "channels": self.channels or [],
            "delivery_status": self.delivery_status or {},
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "issue_title": self.issue.title if self.issue else None,
            "href": self._href(),
        }

    def _href(self) -> str | None:
        if not self.issue_id:
            return None
        if self.alert_type == "content_ready":
            return f"/konten?issue_id={self.issue_id}"
        if self.alert_type == "content_review":
            content_id = (self.delivery_status or {}).get("content_id")
            if content_id:
                return f"/konten/{content_id}"
        return f"/issues/{self.issue_id}"

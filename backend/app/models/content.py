"""Content production and approval models."""

from datetime import datetime, timezone

from app.extensions import db


class ContentItem(db.Model):
    __tablename__ = "content_items"

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey("issues.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)
    # text_release | infographic | video
    body = db.Column(db.Text)
    media_url = db.Column(db.String(500))
    status = db.Column(db.String(50), default="draft", nullable=False)
    # draft | in_review | approved | rejected | published
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    issue = db.relationship("Issue", back_populates="content_items")
    approvals = db.relationship(
        "ContentApproval", back_populates="content_item", cascade="all, delete-orphan"
    )

    def to_dict(self, include_approvals: bool = False):
        data = {
            "id": self.id,
            "issue_id": self.issue_id,
            "title": self.title,
            "content_type": self.content_type,
            "body": self.body,
            "media_url": self.media_url,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_approvals:
            data["approvals"] = [a.to_dict() for a in self.approvals]
        return data


class ContentApproval(db.Model):
    __tablename__ = "content_approvals"

    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey("content_items.id"), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    decision = db.Column(db.String(50), nullable=False)  # approved | rejected
    notes = db.Column(db.Text)
    decided_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    content_item = db.relationship("ContentItem", back_populates="approvals")

    def to_dict(self):
        return {
            "id": self.id,
            "content_id": self.content_id,
            "reviewer_id": self.reviewer_id,
            "decision": self.decision,
            "notes": self.notes,
            "decided_at": self.decided_at.isoformat() if self.decided_at else None,
        }

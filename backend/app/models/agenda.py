"""F.09 Agenda Setting — editorial calendar items."""

from datetime import datetime, timezone

from app.extensions import db


class EditorialAgenda(db.Model):
    __tablename__ = "editorial_agendas"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    theme = db.Column(db.String(100))  # pembangunan | penghargaan | sosial | lainnya
    planned_date = db.Column(db.Date, nullable=False, index=True)
    channel = db.Column(db.String(50), default="media")  # media | sosial | both
    status = db.Column(db.String(50), default="planned", nullable=False)
    # planned | in_production | ready | published | cancelled
    target_media = db.Column(db.String(255))
    content_id = db.Column(db.Integer, db.ForeignKey("content_items.id"))
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    notes = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "theme": self.theme,
            "planned_date": self.planned_date.isoformat() if self.planned_date else None,
            "channel": self.channel,
            "status": self.status,
            "target_media": self.target_media,
            "content_id": self.content_id,
            "created_by": self.created_by,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

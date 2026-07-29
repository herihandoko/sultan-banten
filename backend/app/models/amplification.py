"""ASN Mission Board and KOL models."""

from datetime import datetime, timezone

from app.extensions import db


class Mission(db.Model):
    __tablename__ = "missions"

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey("issues.id"))
    title = db.Column(db.String(255), nullable=False)
    instruction = db.Column(db.Text, nullable=False)
    target_url = db.Column(db.String(500))
    action_type = db.Column(db.String(50))  # like | share | comment
    target_count = db.Column(db.Integer, default=0)
    starts_at = db.Column(db.DateTime)
    ends_at = db.Column(db.DateTime)
    status = db.Column(db.String(50), default="active")  # active | completed | cancelled
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    participations = db.relationship(
        "MissionParticipation", back_populates="mission", cascade="all, delete-orphan"
    )

    def to_dict(self, include_stats: bool = False):
        data = {
            "id": self.id,
            "issue_id": self.issue_id,
            "title": self.title,
            "instruction": self.instruction,
            "target_url": self.target_url,
            "action_type": self.action_type,
            "target_count": self.target_count,
            "starts_at": self.starts_at.isoformat() if self.starts_at else None,
            "ends_at": self.ends_at.isoformat() if self.ends_at else None,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_stats:
            data["participation_count"] = len(self.participations)
        return data


class MissionParticipation(db.Model):
    __tablename__ = "mission_participation"

    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer, db.ForeignKey("missions.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    opd_name = db.Column(db.String(150))
    proof_url = db.Column(db.String(500))
    notes = db.Column(db.Text)
    completed_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    mission = db.relationship("Mission", back_populates="participations")

    def to_dict(self):
        return {
            "id": self.id,
            "mission_id": self.mission_id,
            "user_id": self.user_id,
            "opd_name": self.opd_name,
            "proof_url": self.proof_url,
            "notes": self.notes,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class KolPartner(db.Model):
    __tablename__ = "kol_partners"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    platform = db.Column(db.String(50))
    handle = db.Column(db.String(100))
    followers = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float, default=0.0)
    topics = db.Column(db.String(255))
    contract_status = db.Column(db.String(50), default="prospect")
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    campaigns = db.relationship("KolCampaign", back_populates="kol", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "platform": self.platform,
            "handle": self.handle,
            "followers": self.followers,
            "engagement_rate": self.engagement_rate,
            "topics": self.topics,
            "contract_status": self.contract_status,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class KolCampaign(db.Model):
    __tablename__ = "kol_campaigns"

    id = db.Column(db.Integer, primary_key=True)
    kol_id = db.Column(db.Integer, db.ForeignKey("kol_partners.id"), nullable=False)
    issue_id = db.Column(db.Integer, db.ForeignKey("issues.id"))
    title = db.Column(db.String(255), nullable=False)
    deliverable_url = db.Column(db.String(500))
    scheduled_at = db.Column(db.DateTime)
    published_at = db.Column(db.DateTime)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    budget = db.Column(db.Numeric(14, 2))
    budget_status = db.Column(db.String(50), default="planned")
    status = db.Column(db.String(50), default="planned")
    notes = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    kol = db.relationship("KolPartner", back_populates="campaigns")

    def to_dict(self):
        return {
            "id": self.id,
            "kol_id": self.kol_id,
            "issue_id": self.issue_id,
            "title": self.title,
            "deliverable_url": self.deliverable_url,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "budget": float(self.budget) if self.budget is not None else None,
            "budget_status": self.budget_status,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

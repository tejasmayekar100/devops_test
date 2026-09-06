from config.database import db
from datetime import datetime


class ApprovalHistory(db.Model):
    __tablename__ = "approval_history"

    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(
        db.Integer,
        db.ForeignKey("expense_claims.id"),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    action = db.Column(db.String(50), nullable=False)
    comment = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.now)  # needs attention

    def to_dict(self):
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "user_id": self.user_id,
            "action": self.action,
            "comment": self.comment,
            "created_at": self.created_at
        }

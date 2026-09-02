from config.database import db


class Reimbursement(db.Model):
    __tablename__ = "reimbursements"

    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(
        db.Integer,
        db.ForeignKey("expense_claims.id"),
        nullable=False
    )
    approved_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    processed_date = db.Column(db.Date)

    def to_dict(self):
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "approved_amount": self.approved_amount,
            "status": self.status,
            "processed_date": self.processed_date
        }

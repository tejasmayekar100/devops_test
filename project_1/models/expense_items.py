from config.database import db


class ExpenseItem(db.Model):
    __tablename__ = "expense_items"

    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(
        db.Integer,
        db.ForeignKey("expense_claims.id"),
        nullable=False
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("expense_categories.id"),
        nullable=False
    )
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    expense_date = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "category_id": self.category_id,
            "description": self.description,
            "amount": self.amount,
            "expense_date": self.expense_date
        }

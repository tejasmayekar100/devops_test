from config.database import db


class ExpensePolicy(db.Model):
    __tablename__ = "expense_policies"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("expense_categories.id"),
        nullable=False
    )
    maximum_amount = db.Column(db.Numeric(10, 2), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "maximum_amount": self.maximum_amount
        }

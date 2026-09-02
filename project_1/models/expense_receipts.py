from config.database import db


class ExpenseReceipt(db.Model):
    __tablename__ = "expense_receipts"

    id = db.Column(db.Integer, primary_key=True)
    expense_item_id = db.Column(
        db.Integer,
        db.ForeignKey("expense_items.id"),
        nullable=False
    )
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "expense_item_id": self.expense_item_id,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_type": self.file_type
        }

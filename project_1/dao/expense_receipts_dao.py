from config.database import db
from models.expense_receipts import ExpenseReceipt
from sqlalchemy.exc import IntegrityError


class ExpenseReceiptDAO:

    def get_all(self, page=1, per_page=10):
        return ExpenseReceipt.query.paginate(page=page, per_page=per_page)

    def get_by_id(self, receipt_id):
        return ExpenseReceipt.query.get(receipt_id)

    def get_by_expense_item_id(self, expense_item_id):
        return ExpenseReceipt.query.filter_by(expense_item_id=expense_item_id).all()

    def save_receipt(self, receipt):
        db.session.add(receipt)
        db.session.commit()
        return receipt

    def update(self, receipt):
        db.session.commit()
        return receipt

    def delete(self, receipt):
        try:
            db.session.delete(receipt)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

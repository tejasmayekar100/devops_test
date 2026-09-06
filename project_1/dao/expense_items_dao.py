from config.database import db
from models.expense_items import ExpenseItem
from sqlalchemy.exc import IntegrityError


class ExpenseItemDAO:

    def get_all(self, page=1, per_page=10):
        return ExpenseItem.query.paginate(page=page, per_page=per_page)

    def get_by_id(self, item_id):
        return ExpenseItem.query.get(item_id)

    def get_by_claim_id(self, claim_id):
        return ExpenseItem.query.filter_by(claim_id=claim_id).all()

    def get_by_category_id(self, category_id):
        return ExpenseItem.query.filter_by(category_id=category_id).all()

    def save_item(self, item):
        db.session.add(item)
        db.session.commit()
        return item

    def update(self, item):
        db.session.commit()
        return item

    def delete(self, item):
        try:
            db.session.delete(item)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

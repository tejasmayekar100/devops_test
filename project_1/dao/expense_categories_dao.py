from config.database import db
from models.expense_categories import ExpenseCategory
from sqlalchemy.exc import IntegrityError


class ExpenseCategoryDAO:

    def get_all(self, page=1, per_page=10):
        return ExpenseCategory.query.paginate(page=page, per_page=per_page)

    def get_by_id(self, category_id):
        return ExpenseCategory.query.get(category_id)

    def get_by_name(self, name):
        return ExpenseCategory.query.filter_by(name=name).first()

    def save_category(self, category):
        db.session.add(category)
        db.session.commit()
        return category

    def update(self, category):
        db.session.commit()
        return category

    def delete(self, category):
        try:
            db.session.delete(category)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

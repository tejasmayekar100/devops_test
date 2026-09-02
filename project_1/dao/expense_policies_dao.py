from config.database import db
from models.expense_policies import ExpensePolicy
from sqlalchemy.exc import IntegrityError


class ExpensePolicyDAO:

    def get_all(self, page=1, per_page=10):
        return ExpensePolicy.query.paginate(page=page, per_page=per_page)

    def get_by_id(self, policy_id):
        return ExpensePolicy.query.get(policy_id)

    def get_by_category_id(self, category_id):
        return ExpensePolicy.query.filter_by(category_id=category_id).first()

    def save_policy(self, policy):
        db.session.add(policy)
        db.session.commit()
        return policy

    def update(self, policy):
        db.session.commit()
        return policy

    def delete(self, policy):
        try:
            db.session.delete(policy)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

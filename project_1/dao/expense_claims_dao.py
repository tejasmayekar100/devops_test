from config.database import db
from models.expense_claims import ExpenseClaim
from sqlalchemy.exc import IntegrityError


class ExpenseClaimDAO:

    def get_all(self, page=1, per_page=10):
        return ExpenseClaim.query.paginate(page=page, per_page=per_page)

    def get_by_id(self, claim_id):
        return ExpenseClaim.query.get(claim_id)

    def get_by_employee_id(self, employee_id):
        return ExpenseClaim.query.filter_by(employee_id=employee_id).all()

    def get_by_travel_request_id(self, travel_request_id):
        return ExpenseClaim.query.filter_by(travel_request_id=travel_request_id).all()

    def get_by_status(self, status):
        return ExpenseClaim.query.filter_by(status=status).all()

    def save_claim(self, claim):
        db.session.add(claim)
        db.session.commit()
        return claim

    def update(self, claim):
        db.session.commit()
        return claim

    def delete(self, claim):
        try:
            db.session.delete(claim)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

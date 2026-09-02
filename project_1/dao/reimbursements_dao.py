from config.database import db
from models.reimbursements import Reimbursement
from sqlalchemy.exc import IntegrityError


class ReimbursementDAO:

    def get_all(self, page=1, per_page=10):
        return Reimbursement.query.paginate(page=page, per_page=per_page)

    def get_by_id(self, reimbursement_id):
        return Reimbursement.query.get(reimbursement_id)

    def get_by_claim_id(self, claim_id):
        return Reimbursement.query.filter_by(claim_id=claim_id).first()

    def get_by_status(self, status):
        return Reimbursement.query.filter_by(status=status).all()

    def save_reimbursement(self, reimbursement):
        db.session.add(reimbursement)
        db.session.commit()
        return reimbursement

    def update(self, reimbursement):
        db.session.commit()
        return reimbursement

    def delete(self, reimbursement):
        try:
            db.session.delete(reimbursement)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

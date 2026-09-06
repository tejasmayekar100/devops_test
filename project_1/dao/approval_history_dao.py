from config.database import db
from models.approval_history import ApprovalHistory


class ApprovalHistoryDAO:

    def get_all(self, page=1, per_page=10):
        return ApprovalHistory.query.paginate(page=page, per_page=per_page)

    def get_by_id(self, approval_id):
        return ApprovalHistory.query.get(approval_id)

    def get_by_claim_id(self, claim_id):
        return ApprovalHistory.query.filter_by(claim_id=claim_id).all()

    def get_by_user_id(self, user_id):
        return ApprovalHistory.query.filter_by(user_id=user_id).all()

    def save_approval(self, approval):
        db.session.add(approval)
        db.session.commit()
        return approval

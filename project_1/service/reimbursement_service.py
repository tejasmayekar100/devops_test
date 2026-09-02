from models.reimbursements import Reimbursement
from datetime import date


class ReimbursementService:

    def __init__(self, reimbursement_dao, expense_claim_dao):
        self.reimbursement_dao = reimbursement_dao
        self.expense_claim_dao = expense_claim_dao

    def get_all_reimbursements(self, page=1, per_page=10):
        return self.reimbursement_dao.get_all(page, per_page)

    def get_reimbursement(self, reimbursement_id):
        reimbursement = self.reimbursement_dao.get_by_id(reimbursement_id)

        if reimbursement is None:
            raise ValueError("Reimbursement not found")

        return reimbursement

    def get_reimbursement_by_claim(self, claim_id):
        reimbursement = self.reimbursement_dao.get_by_claim_id(claim_id)

        if reimbursement is None:
            raise ValueError("Reimbursement not found")

        return reimbursement

    def create_reimbursement(self, claim_id):
        claim = self.expense_claim_dao.get_by_id(claim_id)

        if claim is None:
            raise ValueError("Expense claim not found")

        if claim.status != "APPROVED":
            raise ValueError("Only approved claims can be reimbursed")

        existing_reimbursement = (
            self.reimbursement_dao.get_by_claim_id(claim_id))

        if existing_reimbursement:
            raise ValueError("Reimbursement already exists for this claim")

        reimbursement = Reimbursement(
            claim_id=claim_id,
            approved_amount=claim.total_amount,
            status="PENDING"
        )

        return self.reimbursement_dao.save_reimbursement(reimbursement)

    def update_reimbursement(self, reimbursement_id, status=None):
        reimbursement = self.reimbursement_dao.get_by_id(reimbursement_id)

        if reimbursement is None:
            raise ValueError("Reimbursement not found")

        if status:
            allowed_statuses = ["PENDING", "PROCESSING", "PAID", "FAILED"]

            status = status.upper()

            if status not in allowed_statuses:
                raise ValueError("Invalid reimbursement status")

            reimbursement.status = status

            if status == "PAID":
                reimbursement.processed_date = date.today()

        return self.reimbursement_dao.update(reimbursement)

    def delete_reimbursement(self, reimbursement_id):
        reimbursement = self.reimbursement_dao.get_by_id(reimbursement_id)

        if not reimbursement:
            return False

        return self.reimbursement_dao.delete(reimbursement)

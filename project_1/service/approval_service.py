from models.approval_history import ApprovalHistory


class ApprovalService:

    def __init__(self, approval_history_dao, expense_claim_dao, employee_dao):
        self.approval_history_dao = approval_history_dao
        self.expense_claim_dao = expense_claim_dao
        self.employee_dao = employee_dao

    def get_all_approval_history(self, page=1, per_page=10):
        return self.approval_history_dao.get_all(page, per_page)

    def get_approval_history(self, approval_id):
        approval = self.approval_history_dao.get_by_id(approval_id)

        if approval is None:
            raise ValueError("Approval record not found")

        return approval

    def get_claim_history(self, claim_id):
        return self.approval_history_dao.get_by_claim_id(claim_id)

    def approve_claim(self, claim_id, user_id, comment=None):
        claim = self.expense_claim_dao.get_by_id(claim_id)

        if claim is None:
            raise ValueError("Expense claim not found")

        if claim.status != "PENDING":
            raise ValueError("Only pending claims can be approved")

        employee = self.employee_dao.get_by_id(claim.employee_id)

        if employee is None:
            raise ValueError("Employee not found")

        manager_employee = self.employee_dao.get_by_user_id(user_id)

        if manager_employee is None:
            raise ValueError("Manager employee profile not found")

        if employee.manager_id != manager_employee.id:
            raise ValueError(
                "Only the employee's manager can approve this claim")

        claim.status = "APPROVED"

        self.expense_claim_dao.update(claim)

        approval = ApprovalHistory(
            claim_id=claim_id,
            user_id=user_id,
            action="APPROVED",
            comment=comment
        )

        return self.approval_history_dao.save_approval(approval)

    def reject_claim(self, claim_id, user_id, comment=None):
        claim = self.expense_claim_dao.get_by_id(claim_id)

        if claim is None:
            raise ValueError("Expense claim not found")

        if claim.status != "PENDING":
            raise ValueError("Only pending claims can be rejected")

        employee = self.employee_dao.get_by_id(claim.employee_id)

        if employee is None:
            raise ValueError("Employee not found")

        manager_employee = self.employee_dao.get_by_user_id(user_id)

        if manager_employee is None:
            raise ValueError("Manager employee profile not found")

        if employee.manager_id != manager_employee.id:
            raise ValueError(
                "Only the employee's manager can reject this claim")

        claim.status = "REJECTED"

        self.expense_claim_dao.update(claim)

        approval = ApprovalHistory(
            claim_id=claim_id,
            user_id=user_id,
            action="REJECTED",
            comment=comment
        )

        return self.approval_history_dao.save_approval(approval)

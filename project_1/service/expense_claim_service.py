from decimal import Decimal

from models.expense_claims import ExpenseClaim
from models.expense_items import ExpenseItem
from models.expense_receipts import ExpenseReceipt


class ExpenseClaimService:
    def __init__(
        self,
        expense_claim_dao,
        expense_item_dao,
        expense_receipt_dao,
        expense_policy_dao,
        travel_request_dao
    ):
        self.expense_claim_dao = expense_claim_dao
        self.expense_item_dao = expense_item_dao
        self.expense_receipt_dao = expense_receipt_dao
        self.expense_policy_dao = expense_policy_dao
        self.travel_request_dao = travel_request_dao

    def get_all_claims(self, page=1, per_page=10):
        return self.expense_claim_dao.get_all(page, per_page)

    def get_claim(self, claim_id):

        claim = self.expense_claim_dao.get_by_id(claim_id)

        if claim is None:
            raise ValueError("Expense claim not found")

        return claim

    def get_employee_claims(self, employee_id):
        return self.expense_claim_dao.get_by_employee_id(employee_id)

    def get_claims_by_travel_request(self, travel_request_id):
        return self.expense_claim_dao.get_by_travel_request_id(travel_request_id)

    def get_claims_by_status(self, status):
        return self.expense_claim_dao.get_by_status(status)

    def create_claim(self, employee_id, travel_request_id, items):
        # Check whether the travel request exists
        travel_request = self.travel_request_dao.get_by_id(travel_request_id)

        if travel_request is None:
            raise ValueError("Travel request not found")

        # Expense claims can only be created against approved travel requests
        if travel_request.status != "APPROVED":
            raise ValueError(
                "Expense claim can only be created for an approved travel request")

        # Check that the travel request belongs to the employee creating the claim
        if travel_request.employee_id != employee_id:
            raise ValueError("Travel request does not belong to this employee")

        if not items:
            raise ValueError("At least one expense item is required")

        total_amount = Decimal("0.00")

        # Validate all expense items before
        # creating the claim
        for item_data in items:
            category_id = item_data["category_id"]

            amount = Decimal(str(item_data["amount"]))

            if amount <= 0:
                raise ValueError("Expense amount must be greater than zero")

            # Get policy for the expense category
            policy = self.expense_policy_dao.get_by_category_id(category_id)

            if policy is None:
                raise ValueError("Expense policy not found for category")

            # Validate expense against policy limit
            if amount > policy.maximum_amount:
                raise ValueError(
                    "Expense amount exceeds the allowed policy limit")

            total_amount += amount

        # Create the main expense claim
        claim = ExpenseClaim(
            employee_id=employee_id,
            travel_request_id=travel_request_id,
            total_amount=total_amount,
            status="PENDING"
        )

        claim = self.expense_claim_dao.save_claim(claim)

        # Create individual expense items
        for item_data in items:

            item = ExpenseItem(
                claim_id=claim.id,
                category_id=item_data["category_id"],
                description=item_data["description"],
                amount=Decimal(str(item_data["amount"])),
                expense_date=item_data["expense_date"]
            )

            self.expense_item_dao.save_item(item)

        return claim

    def get_claim_items(self, claim_id):

        claim = self.expense_claim_dao.get_by_id(claim_id)

        if claim is None:
            raise ValueError("Expense claim not found")

        return self.expense_item_dao.get_by_claim_id(claim_id)

    def update_claim(self, claim_id, status=None):
        claim = self.expense_claim_dao.get_by_id(claim_id)

        if claim is None:
            raise ValueError("Expense claim not found")

        # Status changes are intentionally not performed here.
        #
        # Claim approval/rejection belongs to ApprovalService and ApprovalController.

        return self.expense_claim_dao.update(claim)

    def delete_claim(self, claim_id):

        claim = self.expense_claim_dao.get_by_id(claim_id)

        if not claim:
            return False

        return self.expense_claim_dao.delete(claim)

    def verify_expense_item_ownership(self, expense_item_id, employee_id):

        item = self.expense_item_dao.get_by_id(expense_item_id)

        if item is None:
            raise ValueError("Expense item not found")

        claim = self.expense_claim_dao.get_by_id(item.claim_id)

        if claim is None:
            raise ValueError("Expense claim not found")

        if claim.employee_id != employee_id:
            raise ValueError("Expense item does not belong to this employee")

        return item

    def add_receipt(
        self,
        expense_item_id,
        file_name,
        file_path,
        file_type,
        employee_id=None
    ):
        # If employee_id is supplied, verify ownership.
        #
        # Finance/Admin operations can omit employee_id
        # after authorization has been performed by the
        # controller.

        if employee_id is not None:
            item = self.verify_expense_item_ownership(
                expense_item_id, employee_id)

        else:
            item = self.expense_item_dao.get_by_id(expense_item_id)

            if item is None:
                raise ValueError("Expense item not found")

        receipt = ExpenseReceipt(
            expense_item_id=expense_item_id,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type
        )

        return self.expense_receipt_dao.save_receipt(receipt)

    def get_receipts(self, expense_item_id, employee_id=None):
        # Employees must pass their employee_id so
        # ownership can be verified.
        #
        # Finance/Admin access can omit employee_id
        # after controller-level RBAC authorization.

        if employee_id is not None:
            self.verify_expense_item_ownership(expense_item_id, employee_id)

        else:
            item = self.expense_item_dao.get_by_id(expense_item_id)

            if item is None:
                raise ValueError("Expense item not found")

        return self.expense_receipt_dao.get_by_expense_item_id(expense_item_id)

    def get_receipt(self, receipt_id):

        receipt = self.expense_receipt_dao.get_by_id(receipt_id)

        if receipt is None:
            raise ValueError("Receipt not found")

        return receipt

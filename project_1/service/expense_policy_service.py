from models.expense_policies import ExpensePolicy


class ExpensePolicyService:

    def __init__(self, expense_policy_dao):
        self.expense_policy_dao = expense_policy_dao

    def get_all_policies(self, page=1, per_page=10):
        return self.expense_policy_dao.get_all(page, per_page)

    def get_policy(self, policy_id):
        policy = self.expense_policy_dao.get_by_id(policy_id)

        if policy is None:
            raise ValueError("Expense policy not found")

        return policy

    def get_policy_by_category(self, category_id):
        policy = self.expense_policy_dao.get_by_category_id(category_id)

        if policy is None:
            raise ValueError("Expense policy not found")

        return policy

    def create_policy(self, category_id, maximum_amount):
        existing_policy = self.expense_policy_dao.get_by_category_id(
            category_id)

        if existing_policy:
            raise ValueError("Expense policy already exists for this category")

        policy = ExpensePolicy(
            category_id=category_id,
            maximum_amount=maximum_amount
        )

        return self.expense_policy_dao.save_policy(policy)

    def update_policy(self, policy_id, maximum_amount=None):
        policy = self.expense_policy_dao.get_by_id(policy_id)

        if policy is None:
            raise ValueError("Expense policy not found")

        if maximum_amount is not None:
            policy.maximum_amount = maximum_amount

        return self.expense_policy_dao.update(policy)

    def delete_policy(self, policy_id):
        policy = self.expense_policy_dao.get_by_id(policy_id)

        if not policy:
            return False

        return self.expense_policy_dao.delete(policy)

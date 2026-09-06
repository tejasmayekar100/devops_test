from models.expense_categories import ExpenseCategory


class ExpenseCategoryService:

    def __init__(self, expense_category_dao):
        self.expense_category_dao = expense_category_dao

    def get_all_categories(self, page=1, per_page=10):
        return self.expense_category_dao.get_all(page, per_page)

    def get_category(self, category_id):
        category = self.expense_category_dao.get_by_id(category_id)

        if category is None:
            raise ValueError("Expense category not found")

        return category

    def get_category_by_name(self, name):
        category = self.expense_category_dao.get_by_name(name)

        if category is None:
            raise ValueError("Expense category not found")

        return category

    def create_category(self, name):
        existing_category = self.expense_category_dao.get_by_name(name)

        if existing_category:
            raise ValueError("Expense category already exists")

        category = ExpenseCategory(name=name)

        return self.expense_category_dao.save_category(category)

    def update_category(self, category_id, name=None):
        category = self.expense_category_dao.get_by_id(category_id)

        if category is None:
            raise ValueError("Expense category not found")

        if name:
            existing_category = self.expense_category_dao.get_by_name(name)

            if existing_category and existing_category.id != category_id:
                raise ValueError("Expense category already exists")

            category.name = name

        return self.expense_category_dao.update(category)

    def delete_category(self, category_id):
        category = self.expense_category_dao.get_by_id(category_id)

        if not category:
            return False

        return self.expense_category_dao.delete(category)

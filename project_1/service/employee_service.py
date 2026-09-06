from models.employees import Employee


class EmployeeService:

    def __init__(self, employee_dao):
        self.employee_dao = employee_dao

    def get_all_employees(self, page=1, per_page=10):
        return self.employee_dao.get_all(page, per_page)

    def get_employee(self, employee_id):
        employee = self.employee_dao.get_by_id(employee_id)

        if employee is None:
            raise ValueError("Employee not found")

        return employee

    def get_employee_by_user(self, user_id):
        employee = self.employee_dao.get_by_user_id(user_id)

        if employee is None:
            raise ValueError("Employee profile not found")

        return employee

    def get_employees_by_manager(self, manager_id):
        return self.employee_dao.get_by_manager_id(manager_id)

    def create_employee(self, user_id, name, department=None, manager_id=None):
        existing_employee = self.employee_dao.get_by_user_id(user_id)

        if existing_employee:
            raise ValueError("Employee profile already exists")

        employee = Employee(
            user_id=user_id,
            name=name,
            department=department,
            manager_id=manager_id
        )

        return self.employee_dao.save_employee(employee)

    def update_employee(
        self,
        employee_id,
        name=None,
        department=None,
        manager_id=None
    ):
        employee = self.employee_dao.get_by_id(employee_id)

        if employee is None:
            raise ValueError("Employee not found")

        if name:
            employee.name = name

        if department:
            employee.department = department

        if manager_id:
            employee.manager_id = manager_id

        return self.employee_dao.update(employee)

    def delete_employee(self, employee_id):
        employee = self.employee_dao.get_by_id(employee_id)

        if not employee:
            return False

        return self.employee_dao.delete(employee)

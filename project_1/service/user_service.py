from models.users import User
from models.employees import Employee


class UserService:

    def __init__(self, user_dao, employee_dao):
        self.user_dao = user_dao
        self.employee_dao = employee_dao

    def register_user(
        self,
        email,
        password,
        role,
        name,
        department=None,
        manager_id=None
    ):
        existing_user = self.user_dao.get_by_email(email)

        if existing_user:
            raise ValueError("Email already exists")

        allowed_roles = ["EMPLOYEE", "MANAGER",
                         "FINANCE_ADMIN", "SYSTEM_ADMIN"]

        role = role.upper()

        if role not in allowed_roles:
            raise ValueError("Invalid role")

        user = User(email=email, role=role)

        user.set_password(password)

        user = self.user_dao.save_user(user)

        employee = Employee(
            user_id=user.id,
            name=name,
            department=department,
            manager_id=manager_id
        )

        self.employee_dao.save_employee(employee)

        return user

    def login_user(self, email, password):
        user = self.user_dao.get_by_email(email)

        if not user or not user.check_password(password):
            raise ValueError("Invalid email or password")

        return user

    def get_user(self, user_id):
        user = self.user_dao.get_by_id(user_id)

        if user is None:
            raise ValueError("User not found")

        return user

    def get_all_users(self, page=1, per_page=10):
        return self.user_dao.get_all(page, per_page)

    def update_user(self, user_id, email=None, role=None):
        user = self.user_dao.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        if email:
            existing_user = self.user_dao.get_by_email(email)

            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already exists")

            user.email = email

        if role:
            allowed_roles = ["EMPLOYEE", "MANAGER",
                             "FINANCE_ADMIN", "SYSTEM_ADMIN"]

            role = role.upper()

            if role not in allowed_roles:
                raise ValueError("Invalid role")

            user.role = role

        return self.user_dao.update(user)

    def delete_user(self, user_id):
        user = self.user_dao.get_by_id(user_id)

        if not user:
            return False

        employee = self.employee_dao.get_by_user_id(user_id)

        if employee:
            self.employee_dao.delete(employee)

        return self.user_dao.delete(user)

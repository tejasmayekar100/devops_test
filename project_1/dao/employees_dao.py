from config.database import db
from models.employees import Employee
from sqlalchemy.exc import IntegrityError


class EmployeeDAO:

    def get_all(self, page=1, per_page=10):
        return Employee.query.paginate(page=page, per_page=per_page)

    def get_by_id(self, employee_id):
        return Employee.query.get(employee_id)

    def get_by_user_id(self, user_id):
        return Employee.query.filter_by(user_id=user_id).first()

    def get_by_manager_id(self, manager_id):
        return Employee.query.filter_by(manager_id=manager_id).all()

    def save_employee(self, employee):
        db.session.add(employee)
        db.session.commit()
        return employee

    def update(self, employee):
        db.session.commit()
        return employee

    def delete(self, employee):
        try:
            db.session.delete(employee)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

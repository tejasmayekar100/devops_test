from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash

from flask_jwt_extended import jwt_required, get_jwt_identity

from service.employee_service import EmployeeService
from dao.employees_dao import EmployeeDAO
from utils.decorators import role_required


employee_bp = Blueprint("employee", __name__)

employee_service = EmployeeService(EmployeeDAO())

# API - GET ALL EMPLOYEES


@employee_bp.route("/api/employees", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_employees():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    employees = employee_service.get_all_employees(page, per_page)

    return jsonify({
        "employees": [employee.to_dict() for employee in employees.items],
        "page": employees.page,
        "per_page": employees.per_page,
        "total": employees.total,
        "pages": employees.pages
    }), 200

# API - GET CURRENT USER'S EMPLOYEE PROFILE


@employee_bp.route("/api/employees/me", methods=["GET"])
@jwt_required()
def get_my_employee_profile():
    user_id = int(get_jwt_identity())
    try:
        employee = employee_service.get_employee_by_user(user_id)

        return jsonify({"employee": employee.to_dict()}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - GET EMPLOYEE BY ID


@employee_bp.route("/api/employees/<int:employee_id>", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_employee(employee_id):
    try:
        employee = employee_service.get_employee(employee_id)

        return jsonify({"employee": employee.to_dict()}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - GET EMPLOYEE BY USER ID


@employee_bp.route("/api/employees/user/<int:user_id>", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_employee_by_user(user_id):
    try:
        employee = employee_service.get_employee_by_user(user_id)

        return jsonify({"employee": employee.to_dict()}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - GET EMPLOYEES BY MANAGER


@employee_bp.route("/api/employees/manager/<int:manager_id>", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_employees_by_manager(manager_id):
    employees = employee_service.get_employees_by_manager(manager_id)

    return jsonify({
        "employees": [employee.to_dict() for employee in employees]
    }), 200

# API - CREATE EMPLOYEE


@employee_bp.route("/api/employees", methods=["POST"])
@role_required("SYSTEM_ADMIN")
def create_employee():
    data = request.get_json()

    user_id = data.get("user_id")
    name = data.get("name")
    department = data.get("department")
    manager_id = data.get("manager_id")

    if not user_id or not name:
        return jsonify({"message": "user_id and name are required"}), 400

    try:
        employee = employee_service.create_employee(
            user_id=user_id,
            name=name,
            department=department,
            manager_id=manager_id
        )

        return jsonify({
            "message": "Employee created successfully",
            "employee": employee.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# API - UPDATE EMPLOYEE


@employee_bp.route("/api/employees/<int:employee_id>", methods=["PUT"])
@role_required("SYSTEM_ADMIN")
def update_employee(employee_id):
    data = request.get_json()

    name = data.get("name")
    department = data.get("department")
    manager_id = data.get("manager_id")

    try:
        employee = employee_service.update_employee(
            employee_id=employee_id,
            name=name,
            department=department,
            manager_id=manager_id
        )

        return jsonify({
            "message": "Employee updated successfully",
            "employee": employee.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# API - DELETE EMPLOYEE


@employee_bp.route("/api/employees/<int:employee_id>", methods=["DELETE"])
@role_required("SYSTEM_ADMIN")
def delete_employee(employee_id):
    try:
        success = employee_service.delete_employee(employee_id)

        if not success:
            return jsonify({"message": "Employee not found"}), 404

        return jsonify({"message": "Employee deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# WEB - LIST EMPLOYEES


@employee_bp.route("/employees", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def web_list_employees():
    page = request.args.get("page", 1, type=int)

    per_page = request.args.get("per_page", 10, type=int)

    employees = employee_service.get_all_employees(page, per_page)

    return render_template(
        "employees/list.html",
        employees=employees
    )

# WEB - DELETE EMPLOYEE


@employee_bp.route("/employees/delete/<int:employee_id>", methods=["POST"])
@role_required("SYSTEM_ADMIN")
def web_delete_employee(employee_id):
    try:
        success = employee_service.delete_employee(employee_id)

        if success:
            flash("Employee deleted successfully!", "success")
        else:
            flash("Employee not found", "danger")

    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("employee.web_list_employees"))

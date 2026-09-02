from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash

from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from service.travel_request_service import TravelRequestService
from service.employee_service import EmployeeService
from dao.travel_request_dao import TravelRequestDAO
from dao.employees_dao import EmployeeDAO

from utils.decorators import role_required


travel_request_bp = Blueprint("travel_request", __name__)


travel_request_service = TravelRequestService(
    TravelRequestDAO(), EmployeeDAO())

employee_service = EmployeeService(EmployeeDAO())

# API - GET ALL TRAVEL REQUESTS


@travel_request_bp.route("/api/travel-requests", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_travel_requests():
    page = request.args.get("page", 1, type=int)

    per_page = request.args.get("per_page", 10, type=int)

    requests = travel_request_service.get_all_travel_requests(page, per_page)

    return jsonify({
        "travel_requests": [travel_request.to_dict() for travel_request in requests.items],
        "page": requests.page,
        "per_page": requests.per_page,
        "total": requests.total,
        "pages": requests.pages
    }), 200

# API - GET MY TRAVEL REQUESTS


@travel_request_bp.route("/api/travel-requests/me", methods=["GET"])
@jwt_required()
def get_my_travel_requests():
    user_id = int(get_jwt_identity())
    try:
        employee = employee_service.get_employee_by_user(user_id)

        requests = travel_request_service.get_employee_requests(employee.id)

        return jsonify({
            "travel_requests": [travel_request.to_dict() for travel_request in requests]
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - GET TRAVEL REQUEST BY ID


@travel_request_bp.route("/api/travel-requests/<int:request_id>", methods=["GET"])
@jwt_required()
def get_travel_request(request_id):
    user_id = int(get_jwt_identity())
    try:
        travel_request = travel_request_service.get_travel_request(request_id)

        employee = employee_service.get_employee_by_user(user_id)

        # Employees can only view their own requests.
        # Managers, Finance Admins and System Admins can view requests belonging to other employees. (inside if)
        if travel_request.employee_id != employee.id:

            claims = get_jwt()
            role = claims.get("role")

            if role not in ["MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN"]:
                return jsonify({"message": "Forbidden"}), 403

        return jsonify({"travel_request": travel_request.to_dict()}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - GET TRAVEL REQUESTS BY EMPLOYEE


@travel_request_bp.route("/api/travel-requests/employee/<int:employee_id>", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_requests_by_employee(employee_id):
    requests = travel_request_service.get_employee_requests(employee_id)

    return jsonify({"travel_requests": [travel_request.to_dict() for travel_request in requests]}), 200

# API - GET TRAVEL REQUESTS BY STATUS


@travel_request_bp.route("/api/travel-requests/status/<string:status>", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_requests_by_status(status):
    requests = travel_request_service.get_requests_by_status(status)

    return jsonify({"travel_requests": [travel_request.to_dict() for travel_request in requests]}), 200

# API - CREATE TRAVEL REQUEST


@travel_request_bp.route("/api/travel-requests", methods=["POST"])
@role_required("EMPLOYEE")
def create_travel_request():
    user_id = int(get_jwt_identity())

    data = request.get_json()

    destination = data.get("destination")
    purpose = data.get("purpose")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    estimated_amount = data.get("estimated_amount")

    if (not destination or not purpose or not start_date or not end_date or estimated_amount is None):
        return jsonify({"message": ("destination, purpose, start_date, end_date and estimated_amount are required")}), 400

    try:
        employee = employee_service.get_employee_by_user(user_id)

        travel_request = travel_request_service.create_travel_request(
            employee_id=employee.id,
            destination=destination,
            purpose=purpose,
            start_date=start_date,
            end_date=end_date,
            estimated_amount=estimated_amount
        )

        return jsonify({
            "message": "Travel request created successfully",
            "travel_request": travel_request.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# API - UPDATE TRAVEL REQUEST


@travel_request_bp.route("/api/travel-requests/<int:request_id>", methods=["PUT"])
@jwt_required()
def update_travel_request(request_id):

    user_id = int(get_jwt_identity())

    data = request.get_json()

    destination = data.get("destination")
    purpose = data.get("purpose")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    estimated_amount = data.get("estimated_amount")

    try:
        employee = employee_service.get_employee_by_user(user_id)

        travel_request = travel_request_service.get_travel_request(request_id)

        if travel_request.employee_id != employee.id:
            return jsonify({"message": "Forbidden"}), 403

        travel_request = travel_request_service.update_travel_request(
            request_id=request_id,
            destination=destination,
            purpose=purpose,
            start_date=start_date,
            end_date=end_date,
            estimated_amount=estimated_amount
        )

        return jsonify({
            "message": "Travel request updated successfully",
            "travel_request": travel_request.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - DELETE TRAVEL REQUEST


@travel_request_bp.route("/api/travel-requests/<int:request_id>", methods=["DELETE"])
@jwt_required()
def delete_travel_request(request_id):
    user_id = int(get_jwt_identity())

    try:
        employee = employee_service.get_employee_by_user(user_id)

        travel_request = travel_request_service.get_travel_request(request_id)

        if travel_request.employee_id != employee.id:
            return jsonify({"message": "Forbidden"}), 403

        success = travel_request_service.delete_travel_request(request_id)

        if not success:
            return jsonify({"message": "Travel request not found"}), 404

        return jsonify({"message": "Travel request deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - APPROVE TRAVEL REQUEST


@travel_request_bp.route("/api/travel-requests/<int:request_id>/approve", methods=["PATCH"])
@role_required("MANAGER")
def approve_travel_request(request_id):

    manager_user_id = int(get_jwt_identity())

    try:
        travel_request = (travel_request_service.approve_travel_request(
            request_id, manager_user_id))

        return jsonify({
            "message": "Travel request approved successfully",
            "travel_request": travel_request.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# API - REJECT TRAVEL REQUEST


@travel_request_bp.route("/api/travel-requests/<int:request_id>/reject", methods=["PATCH"])
@role_required("MANAGER")
def reject_travel_request(request_id):
    manager_user_id = int(get_jwt_identity())

    try:
        travel_request = (travel_request_service.reject_travel_request(
            request_id, manager_user_id))

        return jsonify({
            "message": "Travel request rejected successfully",
            "travel_request": travel_request.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# WEB - LIST TRAVEL REQUESTS


@travel_request_bp.route("/travel-requests", methods=["GET"])
@role_required("EMPLOYEE", "MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def web_list_travel_requests():
    page = request.args.get("page", 1, type=int)

    per_page = request.args.get("per_page", 10, type=int)

    claims = get_jwt()
    role = claims.get("role")

    if role == "EMPLOYEE":
        user_id = int(get_jwt_identity())
        try:
            employee = employee_service.get_employee_by_user(user_id)

            requests = travel_request_service.get_employee_requests(
                employee.id)

        except ValueError as e:
            flash(str(e), "danger")

            return redirect(url_for("auth.web_home"))

    else:
        requests = travel_request_service.get_all_travel_requests(
            page, per_page)

    return render_template(
        "travel_requests/list.html",
        travel_requests=requests,
        current_user=get_jwt()
    )

# WEB - CREATE TRAVEL REQUEST


@travel_request_bp.route("/travel-requests/add", methods=["GET", "POST"])
@role_required("EMPLOYEE")
def web_create_travel_request():
    if request.method == "POST":
        data = request.form

        destination = data.get("destination", "").strip()

        purpose = data.get("purpose", "").strip()

        start_date = data.get("start_date")

        end_date = data.get("end_date")

        estimated_amount = data.get("estimated_amount")

        try:
            user_id = int(get_jwt_identity())

            employee = employee_service.get_employee_by_user(user_id)

            travel_request_service.create_travel_request(
                employee_id=employee.id,
                destination=destination,
                purpose=purpose,
                start_date=start_date,
                end_date=end_date,
                estimated_amount=estimated_amount
            )

            flash("Travel request created successfully!", "success")

            return redirect(url_for("travel_request.web_list_travel_requests"))

        except ValueError as e:
            flash(str(e), "danger")

    return render_template("travel_requests/add.html")


# ============================================================
# WEB - APPROVE TRAVEL REQUEST
# ============================================================

@travel_request_bp.route(
    "/travel-requests/<int:request_id>/approve",
    methods=["POST"]
)
@role_required("MANAGER")
def web_approve_travel_request(request_id):

    manager_user_id = int(get_jwt_identity())

    try:
        travel_request_service.approve_travel_request(
            request_id,
            manager_user_id
        )

        flash("Travel request approved successfully!", "success")

    except ValueError as e:

        flash(str(e), "danger")

    return redirect(
        url_for("travel_request.web_list_travel_requests")
    )


# ============================================================
# WEB - REJECT TRAVEL REQUEST
# ============================================================

@travel_request_bp.route(
    "/travel-requests/<int:request_id>/reject",
    methods=["POST"]
)
@role_required("MANAGER")
def web_reject_travel_request(request_id):

    manager_user_id = int(get_jwt_identity())

    try:
        travel_request_service.reject_travel_request(
            request_id,
            manager_user_id
        )

        flash("Travel request rejected successfully!", "success")

    except ValueError as e:

        flash(str(e), "danger")

    return redirect(
        url_for("travel_request.web_list_travel_requests")
    )


# WEB - DELETE TRAVEL REQUEST


@travel_request_bp.route("/travel-requests/delete/<int:request_id>", methods=["POST"])
@role_required("EMPLOYEE")
def web_delete_travel_request(request_id):
    try:
        user_id = int(get_jwt_identity())

        employee = employee_service.get_employee_by_user(user_id)

        travel_request = travel_request_service.get_travel_request(request_id)

        if travel_request.employee_id != employee.id:
            flash("You are not allowed to delete this travel request.", "danger")

            return redirect(url_for("travel_request.web_list_travel_requests"))

        success = travel_request_service.delete_travel_request(request_id)

        if success:
            flash("Travel request deleted successfully!", "success")

        else:
            flash("Travel request not found", "danger")

    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("travel_request.web_list_travel_requests"))

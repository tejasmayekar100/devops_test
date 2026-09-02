from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash

from flask_jwt_extended import jwt_required, get_jwt_identity

from service.reimbursement_service import ReimbursementService
from service.employee_service import EmployeeService

from dao.reimbursements_dao import ReimbursementDAO
from dao.expense_claims_dao import ExpenseClaimDAO
from dao.employees_dao import EmployeeDAO

from utils.decorators import role_required

reimbursement_bp = Blueprint("reimbursement", __name__)

reimbursement_dao = ReimbursementDAO()
expense_claim_dao = ExpenseClaimDAO()
employee_dao = EmployeeDAO()

reimbursement_service = ReimbursementService(
    reimbursement_dao,
    expense_claim_dao
)

employee_service = EmployeeService(employee_dao)

# API - GET ALL REIMBURSEMENTS


@reimbursement_bp.route("/api/reimbursements", methods=["GET"])
@role_required("FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_reimbursements():
    page = request.args.get("page", 1, type=int)

    per_page = request.args.get("per_page", 10, type=int)

    reimbursements = (
        reimbursement_service.get_all_reimbursements(page, per_page))

    return jsonify({"reimbursements": [reimbursement.to_dict() for reimbursement in reimbursements.items],
                    "page": reimbursements.page,
                    "per_page": reimbursements.per_page,
                    "total": reimbursements.total,
                    "pages": reimbursements.pages
                    }), 200


# API - GET REIMBURSEMENT BY ID
@reimbursement_bp.route("/api/reimbursements/<int:reimbursement_id>", methods=["GET"])
@role_required("FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_reimbursement(reimbursement_id):
    try:
        reimbursement = (
            reimbursement_service.get_reimbursement(reimbursement_id))

        return jsonify({"reimbursement": reimbursement.to_dict()}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404


# API - GET REIMBURSEMENT BY CLAIM
@reimbursement_bp.route("/api/expense-claims/<int:claim_id>/reimbursement", methods=["GET"])
@role_required("FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_reimbursement_by_claim(claim_id):
    try:
        reimbursement = (
            reimbursement_service.get_reimbursement_by_claim(claim_id))

        return jsonify({"reimbursement": reimbursement.to_dict()}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404


# API - GET MY REIMBURSEMENT
@reimbursement_bp.route("/api/expense-claims/<int:claim_id>/reimbursement/me", methods=["GET"])
@jwt_required()
def get_my_reimbursement(claim_id):
    user_id = int(get_jwt_identity())

    try:
        employee = (
            employee_service.get_employee_by_user(user_id))

        claim = expense_claim_dao.get_by_id(claim_id)

        if claim is None:
            return jsonify({"message": "Expense claim not found"}), 404

        if claim.employee_id != employee.id:
            return jsonify({"message": "Forbidden"}), 403

        reimbursement = (
            reimbursement_service.get_reimbursement_by_claim(claim_id))

        return jsonify({"reimbursement": reimbursement.to_dict()}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404


# API - CREATE REIMBURSEMENT
@reimbursement_bp.route("/api/expense-claims/<int:claim_id>/reimbursement", methods=["POST"])
@role_required("FINANCE_ADMIN")
def create_reimbursement(claim_id):
    try:
        reimbursement = (reimbursement_service.create_reimbursement(claim_id))

        return jsonify({
            "message": "Reimbursement created successfully",
            "reimbursement": reimbursement.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"message": str(e)}), 400


# API - UPDATE REIMBURSEMENT STATUS
@reimbursement_bp.route("/api/reimbursements/<int:reimbursement_id>", methods=["PATCH"])
@role_required("FINANCE_ADMIN")
def update_reimbursement(reimbursement_id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    status = data.get("status")

    if status is None:
        return jsonify({"message": "Status is required"}), 400

    if not isinstance(status, str):
        return jsonify({"message": "Status must be a valid string"}), 400

    status = status.strip().upper()

    allowed_statuses = ["PENDING", "PROCESSING", "PAID", "FAILED"]

    if status not in allowed_statuses:
        return jsonify({"message": "Invalid reimbursement status"}), 400

    try:
        reimbursement = (reimbursement_service.update_reimbursement(
            reimbursement_id, status=status))

        return jsonify({
            "message": "Reimbursement updated successfully",
            "reimbursement": reimbursement.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400


# API - DELETE REIMBURSEMENT
@reimbursement_bp.route("/api/reimbursements/<int:reimbursement_id>", methods=["DELETE"])
@role_required("FINANCE_ADMIN", "SYSTEM_ADMIN")
def delete_reimbursement(reimbursement_id):
    try:
        reimbursement = (
            reimbursement_service.get_reimbursement(reimbursement_id))

        # Paid reimbursements are completed financial records
        # and should not be deleted.
        if reimbursement.status == "PAID":
            return jsonify({"message": "Paid reimbursements cannot be deleted"}), 400

        success = (reimbursement_service.delete_reimbursement(reimbursement_id))

        if not success:
            return jsonify({"message": "Reimbursement not found"}), 404

        return jsonify({"message": "Reimbursement deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404


# WEB - LIST REIMBURSEMENTS
@reimbursement_bp.route("/reimbursements", methods=["GET"])
@role_required("FINANCE_ADMIN", "SYSTEM_ADMIN")
def web_list_reimbursements():
    page = request.args.get("page", 1, type=int)

    per_page = request.args.get("per_page", 10, type=int)

    reimbursements = (
        reimbursement_service.get_all_reimbursements(page, per_page))

    return render_template(
        "reimbursements/list.html",
        reimbursements=reimbursements
    )


# WEB - VIEW REIMBURSEMENT
@reimbursement_bp.route("/reimbursements/<int:reimbursement_id>", methods=["GET"])
@role_required("FINANCE_ADMIN", "SYSTEM_ADMIN")
def web_view_reimbursement(reimbursement_id):
    try:
        reimbursement = (
            reimbursement_service.get_reimbursement(reimbursement_id))

        return render_template(
            "reimbursements/detail.html",
            reimbursement=reimbursement
        )

    except ValueError as e:
        flash(str(e), "danger")

        return redirect(url_for("reimbursement.web_list_reimbursements"))


# WEB - VIEW MY REIMBURSEMENT
@reimbursement_bp.route("/my-claims/<int:claim_id>/reimbursement", methods=["GET"])
@role_required("EMPLOYEE")
def web_my_reimbursement(claim_id):
    user_id = int(get_jwt_identity())

    try:
        employee = (
            employee_service.get_employee_by_user(user_id))

        claim = expense_claim_dao.get_by_id(claim_id)

        if claim is None:
            flash("Expense claim not found", "danger")

            return redirect(url_for("auth.web_home"))

        if claim.employee_id != employee.id:
            flash(
                "You do not have permission to view this claim",
                "danger"
            )

            return redirect(url_for("auth.web_home"))

        reimbursement = (
            reimbursement_service.get_reimbursement_by_claim(claim_id))

        return render_template(
            "reimbursements/my_status.html",
            reimbursement=reimbursement,
            claim=claim
        )

    except ValueError as e:
        flash(str(e), "danger")

        return redirect(url_for("auth.web_home"))


# WEB - CREATE REIMBURSEMENT
@reimbursement_bp.route("/expense-claims/<int:claim_id>/reimbursement", methods=["POST"])
@role_required("FINANCE_ADMIN")
def web_create_reimbursement(claim_id):
    try:
        reimbursement = (reimbursement_service.create_reimbursement(claim_id))

        flash("Reimbursement created successfully!", "success")

    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("reimbursement.web_list_reimbursements"))

# WEB - UPDATE REIMBURSEMENT


@reimbursement_bp.route("/reimbursements/<int:reimbursement_id>/update", methods=["POST"])
@role_required("FINANCE_ADMIN")
def web_update_reimbursement(reimbursement_id):
    status = request.form.get("status", "").strip().upper()

    allowed_statuses = ["PENDING", "PROCESSING", "PAID", "FAILED"]

    if status not in allowed_statuses:
        flash("Invalid reimbursement status", "danger")

        return redirect(
            url_for(
                "reimbursement.web_view_reimbursement",
                reimbursement_id=reimbursement_id
            )
        )

    try:
        reimbursement_service.update_reimbursement(
            reimbursement_id, status=status)

        flash("Reimbursement updated successfully!", "success")

    except ValueError as e:
        flash(str(e), "danger")

    return redirect(
        url_for(
            "reimbursement.web_view_reimbursement",
            reimbursement_id=reimbursement_id
        )
    )

# WEB - DELETE REIMBURSEMENT


@reimbursement_bp.route("/reimbursements/<int:reimbursement_id>/delete", methods=["POST"])
@role_required("FINANCE_ADMIN", "SYSTEM_ADMIN")
def web_delete_reimbursement(reimbursement_id):
    try:
        reimbursement = (
            reimbursement_service.get_reimbursement(reimbursement_id))

        if reimbursement.status == "PAID":
            flash("Paid reimbursements cannot be deleted", "danger")

            return redirect(
                url_for(
                    "reimbursement.web_view_reimbursement",
                    reimbursement_id=reimbursement_id
                )
            )

        success = (reimbursement_service.delete_reimbursement(reimbursement_id))

        if success:
            flash("Reimbursement deleted successfully!", "success")

        else:
            flash("Reimbursement not found", "danger")

    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("reimbursement.web_list_reimbursements"))

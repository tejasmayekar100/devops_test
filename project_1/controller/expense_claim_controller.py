import os
from uuid import uuid4

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, send_file, current_app

from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from werkzeug.utils import secure_filename

from service.expense_claim_service import ExpenseClaimService
from service.employee_service import EmployeeService

from dao.expense_claims_dao import ExpenseClaimDAO
from dao.expense_items_dao import ExpenseItemDAO
from dao.expense_receipts_dao import ExpenseReceiptDAO
from dao.expense_policies_dao import ExpensePolicyDAO
from dao.travel_request_dao import TravelRequestDAO
from dao.employees_dao import EmployeeDAO

from utils.decorators import role_required

expense_claim_bp = Blueprint("expense_claim", __name__)

expense_claim_service = ExpenseClaimService(
    ExpenseClaimDAO(),
    ExpenseItemDAO(),
    ExpenseReceiptDAO(),
    ExpensePolicyDAO(),
    TravelRequestDAO()
)

employee_service = EmployeeService(EmployeeDAO())

# FILE UPLOAD CONFIGURATION
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

MAX_FILE_SIZE = 5 * 1024 * 1024


def allowed_file(filename):
    """
    Check whether the uploaded file has an allowed extension.
    """
    return ("." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS)


def get_receipt_upload_folder():

    return current_app.config.get("RECEIPT_UPLOAD_FOLDER", os.path.join("uploads", "receipts"))


def save_uploaded_receipt(file):
    """
    Validate and save an uploaded receipt.
    Returns:
        original filename,
        saved path,
        file content type
    """
    if file is None:
        raise ValueError("No file provided")

    if not file.filename:
        raise ValueError("No file selected")

    if not allowed_file(file.filename):
        raise ValueError("Only PDF, PNG, JPG and JPEG files are allowed")

    # Check actual uploaded file size.
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise ValueError("File exceeds the maximum size of 5MB")

    original_filename = secure_filename(file.filename)

    if not original_filename:
        raise ValueError("Invalid file name")

    extension = original_filename.rsplit(".", 1)[1].lower()

    # Generate a unique server-side filename.
    unique_filename = (f"{uuid4().hex}.{extension}")

    upload_folder = get_receipt_upload_folder()

    os.makedirs(upload_folder, exist_ok=True)

    save_path = os.path.join(upload_folder, unique_filename)

    file.save(save_path)

    return (original_filename, save_path, file.content_type)


def can_access_claim(claim, user_id, role):

    if role in ["FINANCE_ADMIN", "SYSTEM_ADMIN"]:
        return True

    employee = employee_service.get_employee_by_user(user_id)

    if role == "EMPLOYEE":
        return claim.employee_id == employee.id

    if role == "MANAGER":
        claim_employee = employee_service.get_employee(claim.employee_id)

        return (claim_employee.manager_id == employee.id)

    return False


def can_access_expense_item(expense_item_id, user_id, role):

    item = expense_claim_service.expense_item_dao.get_by_id(expense_item_id)

    if item is None:
        raise ValueError("Expense item not found")

    claim = expense_claim_service.get_claim(item.claim_id)

    return can_access_claim(claim, user_id, role)

# API - GET ALL EXPENSE CLAIMS


@expense_claim_bp.route("/api/expense-claims", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_claims():
    page = request.args.get("page", 1, type=int)

    per_page = request.args.get("per_page", 10, type=int)

    claims = expense_claim_service.get_all_claims(page, per_page)

    return jsonify({
        "expense_claims": [claim.to_dict() for claim in claims.items],
        "page": claims.page,
        "per_page": claims.per_page,
        "total": claims.total,
        "pages": claims.pages
    }), 200

# API - GET MY EXPENSE CLAIMS


@expense_claim_bp.route("/api/expense-claims/me", methods=["GET"])
@jwt_required()
def get_my_claims():
    user_id = int(get_jwt_identity())

    try:
        employee = employee_service.get_employee_by_user(user_id)

        claims = expense_claim_service.get_employee_claims(employee.id)

        return jsonify({"expense_claims": [claim.to_dict() for claim in claims]}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - GET EXPENSE CLAIM BY ID


@expense_claim_bp.route("/api/expense-claims/<int:claim_id>", methods=["GET"])
@jwt_required()
def get_claim(claim_id):
    user_id = int(get_jwt_identity())

    claims = get_jwt()
    role = claims.get("role")

    try:
        claim = expense_claim_service.get_claim(claim_id)

        if not can_access_claim(claim, user_id, role):
            return jsonify({"message": "Forbidden"}), 403

        return jsonify({"expense_claim": claim.to_dict()}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - GET CLAIMS BY TRAVEL REQUEST


@expense_claim_bp.route("/api/expense-claims/travel-request/<int:travel_request_id>", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_claims_by_travel_request(travel_request_id):
    claims = (
        expense_claim_service
        .get_claims_by_travel_request(travel_request_id)
    )

    return jsonify({"expense_claims": [claim.to_dict() for claim in claims]}), 200

# API - GET CLAIMS BY STATUS


@expense_claim_bp.route("/api/expense-claims/status/<string:status>", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_claims_by_status(status):
    claims = (
        expense_claim_service
        .get_claims_by_status(status)
    )

    return jsonify({"expense_claims": [claim.to_dict() for claim in claims]}), 200

# API - CREATE EXPENSE CLAIM


@expense_claim_bp.route("/api/expense-claims", methods=["POST"])
@role_required("EMPLOYEE")
def create_claim():
    user_id = int(get_jwt_identity())

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    travel_request_id = data.get("travel_request_id")

    items = data.get("items")

    if travel_request_id is None:
        return jsonify({"message": "Travel request ID is required"}), 400

    if items is None:
        return jsonify({"message": "Expense items are required"}), 400

    try:
        travel_request_id = int(travel_request_id)

    except (TypeError, ValueError):
        return jsonify({"message": "Travel request ID must be a valid integer"}), 400

    if not isinstance(items, list):
        return jsonify({"message": "Expense items must be a list"}), 400

    for item in items:
        if not isinstance(item, dict):
            return jsonify({"message": "Each expense item must be an object"}), 400

        required_fields = ["category_id",
                           "description", "amount", "expense_date"]

        for field in required_fields:
            if field not in item:
                return jsonify({"message": f"Expense item field {field} is required"}), 400

        try:
            item["category_id"] = int(item["category_id"])

        except (TypeError, ValueError):
            return jsonify({"message": "Expense item category ID must be a valid integer"}), 400

        try:
            amount = float(item["amount"])

            if amount <= 0:
                return jsonify({"message": "Expense amount must be greater than zero"}), 400

        except (TypeError, ValueError):
            return jsonify({"message": "Expense item amount must be a valid number"}), 400

    try:
        employee = employee_service.get_employee_by_user(user_id)

        claim = expense_claim_service.create_claim(
            employee_id=employee.id,
            travel_request_id=travel_request_id,
            items=items
        )

        return jsonify({
            "message": "Expense claim created successfully",
            "expense_claim": claim.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# API - GET EXPENSE CLAIM ITEMS


@expense_claim_bp.route("/api/expense-claims/<int:claim_id>/items", methods=["GET"])
@jwt_required()
def get_claim_items(claim_id):
    user_id = int(get_jwt_identity())

    claims = get_jwt()
    role = claims.get("role")

    try:
        claim = expense_claim_service.get_claim(claim_id)

        if not can_access_claim(claim, user_id, role):
            return jsonify({"message": "Forbidden"}), 403

        items = expense_claim_service.get_claim_items(claim_id)

        return jsonify({"expense_items": [item.to_dict() for item in items]}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - DELETE EXPENSE CLAIM


@expense_claim_bp.route("/api/expense-claims/<int:claim_id>", methods=["DELETE"])
@role_required("EMPLOYEE")
def delete_claim(claim_id):

    user_id = int(get_jwt_identity())

    try:
        employee = employee_service.get_employee_by_user(user_id)

        claim = expense_claim_service.get_claim(claim_id)

        if claim.employee_id != employee.id:
            return jsonify({"message": "Forbidden"}), 403

        if claim.status != "PENDING":
            return jsonify({"message": "Only pending expense claims can be deleted"}), 400

        success = expense_claim_service.delete_claim(claim_id)

        if not success:
            return jsonify({"message": "Expense claim not found"}), 404

        return jsonify({"message": "Expense claim deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - UPLOAD RECEIPT


@expense_claim_bp.route("/api/expense-items/<int:expense_item_id>/receipts", methods=["POST"])
@role_required("EMPLOYEE")
def add_receipt(expense_item_id):
    user_id = int(get_jwt_identity())

    saved_path = None

    try:
        employee = employee_service.get_employee_by_user(user_id)
        # ----------------------------------------------------
        # request.files is used because this endpoint
        # receives an actual multipart/form-data file.
        # ----------------------------------------------------
        if "file" not in request.files:
            return jsonify({"message": "No file provided"}), 400

        file = request.files["file"]
        # ----------------------------------------------------
        # Verify that the expense item belongs to
        # the logged-in employee.
        # ----------------------------------------------------
        expense_claim_service.verify_expense_item_ownership(
            expense_item_id, employee.id)
        # ----------------------------------------------------
        # Validate and save the actual file.
        # ----------------------------------------------------
        (
            original_filename,
            saved_path,
            file_type
        ) = save_uploaded_receipt(file)

        # ----------------------------------------------------
        # Save receipt metadata in the database.
        # ----------------------------------------------------

        receipt = expense_claim_service.add_receipt(
            expense_item_id=expense_item_id,
            file_name=original_filename,
            file_path=saved_path,
            file_type=file_type,
            employee_id=employee.id
        )

        return jsonify({
            "message": "Receipt uploaded successfully",
            "receipt": receipt.to_dict()
        }), 201

    except ValueError as e:
        # If the file was already saved but a later
        # validation/database operation failed,
        # remove the orphaned file.
        if saved_path and os.path.exists(saved_path):
            os.remove(saved_path)

        return jsonify({"message": str(e)}), 400

    except Exception:
        if saved_path and os.path.exists(saved_path):
            os.remove(saved_path)

        return jsonify({"message": "Failed to upload receipt"}), 500

# API - GET RECEIPTS FOR EXPENSE ITEM


@expense_claim_bp.route("/api/expense-items/<int:expense_item_id>/receipts", methods=["GET"])
@jwt_required()
def get_receipts(expense_item_id):
    user_id = int(get_jwt_identity())

    claims = get_jwt()
    role = claims.get("role")

    try:
        # ----------------------------------------------------
        # Employees can see only their own receipts.
        # Managers can see receipts belonging to employees
        # they manage.
        # Finance/System Admin can access all receipts.
        # ----------------------------------------------------

        item = (
            expense_claim_service
            .expense_item_dao
            .get_by_id(expense_item_id)
        )

        if item is None:
            return jsonify({"message": "Expense item not found"}), 404

        claim = expense_claim_service.get_claim(item.claim_id)

        if not can_access_claim(claim, user_id, role):

            return jsonify({"message": "Forbidden"}), 403

        employee_id = None

        if role == "EMPLOYEE":

            employee = (employee_service.get_employee_by_user(user_id))

            employee_id = employee.id

        elif role == "MANAGER":

            employee = (employee_service.get_employee_by_user(user_id))

            employee_id = claim.employee_id

            claim_employee_manager_id = employee_service.get_employee(
                claim.employee_id).manager_id

            if claim_employee_manager_id != employee.id:
                return jsonify({"message": "Forbidden"}), 403

        receipts = expense_claim_service.get_receipts(
            expense_item_id,
            employee_id=employee_id
        )

        return jsonify({"receipts": [receipt.to_dict() for receipt in receipts]}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - DOWNLOAD RECEIPT


@expense_claim_bp.route("/api/receipts/<int:receipt_id>/download", methods=["GET"])
@role_required("FINANCE_ADMIN", "SYSTEM_ADMIN")
def download_receipt(receipt_id):
    try:
        receipt = expense_claim_service.get_receipt(receipt_id)

        if not os.path.isfile(receipt.file_path):
            return jsonify({"message": "Receipt file not found"}), 404

        return send_file(
            receipt.file_path,
            as_attachment=True,
            download_name=receipt.file_name
        )

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# WEB - LIST EXPENSE CLAIMS


@expense_claim_bp.route("/expense-claims", methods=["GET"])
@role_required("EMPLOYEE", "MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def web_list_claims():
    claims = get_jwt()
    role = claims.get("role")
    try:
        if role == "EMPLOYEE":
            user_id = int(get_jwt_identity())

            employee = (employee_service.get_employee_by_user(user_id))

            expense_claims = (
                expense_claim_service.get_employee_claims(employee.id))

        else:
            page = request.args.get("page", 1, type=int)

            per_page = request.args.get("per_page", 10, type=int)

            expense_claims = (
                expense_claim_service.get_all_claims(page, per_page))

        return render_template(
            "expense_claims/list.html",
            expense_claims=expense_claims,
            current_user=get_jwt()
        )

    except ValueError as e:
        flash(str(e), "danger")

        return redirect(url_for("auth.web_login"))

# WEB - CREATE EXPENSE CLAIM


@expense_claim_bp.route("/expense-claims/add", methods=["GET", "POST"])
@role_required("EMPLOYEE")
def web_create_claim():

    if request.method == "POST":
        travel_request_id = request.form.get("travel_request_id", "").strip()

        if not travel_request_id:
            flash("Travel request ID is required", "danger")

            return render_template("expense_claims/add.html")

        try:
            travel_request_id = int(travel_request_id)

        except ValueError:
            flash("Travel request ID must be a valid integer", "danger")

            return render_template("expense_claims/add.html")

        category_ids = request.form.getlist("category_id")

        descriptions = request.form.getlist("description")

        amounts = request.form.getlist("amount")

        expense_dates = request.form.getlist("expense_date")

        if not category_ids:
            flash("At least one expense item is required", "danger")

            return render_template("expense_claims/add.html")

        if not (len(category_ids) == len(descriptions) == len(amounts) == len(expense_dates)):
            flash("Invalid expense item data", "danger")

            return render_template("expense_claims/add.html")

        try:
            items = []

            for index in range(len(category_ids)):
                items.append({
                    "category_id": int(category_ids[index]),
                    "description": (descriptions[index].strip()),
                    "amount": amounts[index],
                    "expense_date": (expense_dates[index])
                })

            user_id = int(get_jwt_identity())

            employee = (employee_service.get_employee_by_user(user_id))

            expense_claim_service.create_claim(
                employee_id=employee.id,
                travel_request_id=travel_request_id,
                items=items
            )

            flash("Expense claim created successfully!", "success")

            return redirect(url_for("expense_claim.web_list_claims"))

        except ValueError as e:
            flash(str(e), "danger")

    return render_template("expense_claims/add.html")

# WEB - UPLOAD RECEIPT


@expense_claim_bp.route("/expense-items/<int:expense_item_id>/receipts", methods=["GET", "POST"])
@role_required("EMPLOYEE")
def web_upload_receipt(expense_item_id):
    user_id = int(get_jwt_identity())

    try:
        employee = (employee_service.get_employee_by_user(user_id))

        # Verify ownership before showing
        # the upload page.
        expense_claim_service.verify_expense_item_ownership(
            expense_item_id, employee.id)

        if request.method == "POST":

            if "file" not in request.files:
                flash("Please select a receipt file", "danger")

                return render_template(
                    "expense_claims/upload_receipt.html",
                    expense_item_id=expense_item_id
                )

            file = request.files["file"]

            saved_path = None

            try:
                (
                    original_filename,
                    saved_path,
                    file_type
                ) = save_uploaded_receipt(file)

                expense_claim_service.add_receipt(
                    expense_item_id=expense_item_id,
                    file_name=original_filename,
                    file_path=saved_path,
                    file_type=file_type,
                    employee_id=employee.id
                )

                flash("Receipt uploaded successfully!", "success")

                return redirect(url_for("expense_claim.web_list_claims"))

            except ValueError as e:
                if (saved_path and os.path.exists(saved_path)):
                    os.remove(saved_path)

                flash(str(e), "danger")

        return render_template(
            "expense_claims/upload_receipt.html",
            expense_item_id=expense_item_id
        )

    except ValueError as e:
        flash(str(e), "danger")

        return redirect(url_for("expense_claim.web_list_claims"))

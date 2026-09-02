from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash

from service.expense_category_service import ExpenseCategoryService
from dao.expense_categories_dao import ExpenseCategoryDAO

from utils.decorators import role_required

expense_category_bp = Blueprint("expense_category", __name__)

expense_category_service = ExpenseCategoryService(ExpenseCategoryDAO())

# API - GET ALL EXPENSE CATEGORIES


@expense_category_bp.route("/api/expense-categories", methods=["GET"])
@role_required("EMPLOYEE", "MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_categories():
    page = request.args.get("page", 1, type=int)

    per_page = request.args.get("per_page", 10, type=int)

    categories = expense_category_service.get_all_categories(page, per_page)

    return jsonify({
        "expense_categories": [category.to_dict() for category in categories.items],
        "page": categories.page,
        "per_page": categories.per_page,
        "total": categories.total,
        "pages": categories.pages
    }), 200

# API - GET EXPENSE CATEGORY BY ID


@expense_category_bp.route("/api/expense-categories/<int:category_id>", methods=["GET"])
@role_required("EMPLOYEE", "MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_category(category_id):
    try:
        category = expense_category_service.get_category(category_id)

        return jsonify({"expense_category": category.to_dict()}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - GET EXPENSE CATEGORY BY NAME


@expense_category_bp.route("/api/expense-categories/name/<string:name>", methods=["GET"])
@role_required("EMPLOYEE", "MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_category_by_name(name):
    try:
        category = expense_category_service.get_category_by_name(name)

        return jsonify({"expense_category": category.to_dict()}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - CREATE EXPENSE CATEGORY


@expense_category_bp.route("/api/expense-categories", methods=["POST"])
@role_required("SYSTEM_ADMIN")
def create_category():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    name = data.get("name")

    if not name or not name.strip():
        return jsonify({"message": "Category name is required"}), 400

    try:
        category = expense_category_service.create_category(name.strip())

        return jsonify({
            "message": "Expense category created successfully",
            "expense_category": category.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# API - UPDATE EXPENSE CATEGORY


@expense_category_bp.route("/api/expense-categories/<int:category_id>", methods=["PUT"])
@role_required("SYSTEM_ADMIN")
def update_category(category_id):
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    name = data.get("name")

    try:
        category = expense_category_service.update_category(
            category_id,
            name=name.strip() if name else None
        )

        return jsonify({
            "message": "Expense category updated successfully",
            "expense_category": category.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# API - DELETE EXPENSE CATEGORY


@expense_category_bp.route("/api/expense-categories/<int:category_id>", methods=["DELETE"])
@role_required("SYSTEM_ADMIN")
def delete_category(category_id):
    try:
        success = expense_category_service.delete_category(category_id)

        if not success:
            return jsonify({"message": "Expense category not found"}), 404

        return jsonify({"message": "Expense category deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# WEB - LIST EXPENSE CATEGORIES


@expense_category_bp.route("/expense-categories", methods=["GET"])
@role_required("EMPLOYEE", "MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def web_list_categories():
    page = request.args.get("page", 1, type=int)

    per_page = request.args.get("per_page", 10, type=int)

    categories = expense_category_service.get_all_categories(page, per_page)

    return render_template(
        "expense_categories/list.html",
        expense_categories=categories
    )

# WEB - ADD EXPENSE CATEGORY


@expense_category_bp.route("/expense-categories/add", methods=["GET", "POST"])
@role_required("SYSTEM_ADMIN")
def web_add_category():
    if request.method == "POST":
        name = request.form.get("name", "").strip()

        if not name:
            flash("Category name is required", "danger")

            return render_template("expense_categories/add.html")

        try:
            expense_category_service.create_category(name)

            flash("Expense category created successfully!", "success")

            return redirect(url_for("expense_category.web_list_categories"))

        except ValueError as e:
            flash(str(e), "danger")

    return render_template("expense_categories/add.html")

# WEB - DELETE EXPENSE CATEGORY


@expense_category_bp.route("/expense-categories/delete/<int:category_id>", methods=["POST"])
@role_required("SYSTEM_ADMIN")
def web_delete_category(category_id):
    try:
        success = expense_category_service.delete_category(category_id)

        if success:
            flash("Expense category deleted successfully!", "success")

        else:
            flash("Expense category not found", "danger")

    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("expense_category.web_list_categories"))

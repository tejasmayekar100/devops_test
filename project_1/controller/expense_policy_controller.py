from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash

from service.expense_policy_service import ExpensePolicyService
from dao.expense_policies_dao import ExpensePolicyDAO

from utils.decorators import role_required

expense_policy_bp = Blueprint("expense_policy", __name__)

expense_policy_service = ExpensePolicyService(ExpensePolicyDAO())

# API - GET ALL EXPENSE POLICIES


@expense_policy_bp.route("/api/expense-policies", methods=["GET"])
@role_required("EMPLOYEE", "MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_policies():
    page = request.args.get("page", 1, type=int)

    per_page = request.args.get("per_page", 10, type=int)

    policies = expense_policy_service.get_all_policies(page, per_page)

    return jsonify({
        "expense_policies": [policy.to_dict() for policy in policies.items],
        "page": policies.page,
        "per_page": policies.per_page,
        "total": policies.total,
        "pages": policies.pages
    }), 200

# API - GET EXPENSE POLICY BY ID


@expense_policy_bp.route("/api/expense-policies/<int:policy_id>", methods=["GET"])
@role_required("EMPLOYEE", "MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_policy(policy_id):
    try:
        policy = expense_policy_service.get_policy(policy_id)

        return jsonify({"expense_policy": policy.to_dict()}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - GET EXPENSE POLICY BY CATEGORY


@expense_policy_bp.route("/api/expense-policies/category/<int:category_id>", methods=["GET"])
@role_required("EMPLOYEE", "MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_policy_by_category(category_id):
    try:
        policy = expense_policy_service.get_policy_by_category(category_id)

        return jsonify({"expense_policy": policy.to_dict()}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - CREATE EXPENSE POLICY


@expense_policy_bp.route("/api/expense-policies", methods=["POST"])
@role_required("SYSTEM_ADMIN")
def create_policy():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body is required"}), 400

    category_id = data.get("category_id")
    maximum_amount = data.get("maximum_amount")

    if category_id is None:
        return jsonify({"message": "Category ID is required"}), 400

    if maximum_amount is None:
        return jsonify({"message": "Maximum amount is required"}), 400

    try:
        category_id = int(category_id)

    except (TypeError, ValueError):
        return jsonify({"message": "Category ID must be a valid integer"}), 400

    try:
        maximum_amount = float(maximum_amount)

        if maximum_amount <= 0:
            return jsonify({"message": "Maximum amount must be greater than zero"}), 400

    except (TypeError, ValueError):
        return jsonify({"message": "Maximum amount must be a valid number"}), 400

    try:
        policy = expense_policy_service.create_policy(
            category_id, maximum_amount)

        return jsonify({
            "message": "Expense policy created successfully",
            "expense_policy": policy.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# API - UPDATE EXPENSE POLICY


@expense_policy_bp.route("/api/expense-policies/<int:policy_id>", methods=["PUT"])
@role_required("SYSTEM_ADMIN")
def update_policy(policy_id):
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    maximum_amount = data.get("maximum_amount")

    if maximum_amount is None:
        return jsonify({"message": "Maximum amount is required"}), 400

    try:
        maximum_amount = float(maximum_amount)

        if maximum_amount <= 0:
            return jsonify({"message": "Maximum amount must be greater than zero"}), 400

    except (TypeError, ValueError):
        return jsonify({"message": "Maximum amount must be a valid number"}), 400

    try:
        policy = expense_policy_service.update_policy(
            policy_id,
            maximum_amount=maximum_amount
        )

        return jsonify({
            "message": "Expense policy updated successfully",
            "expense_policy": policy.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - DELETE EXPENSE POLICY


@expense_policy_bp.route("/api/expense-policies/<int:policy_id>", methods=["DELETE"])
@role_required("SYSTEM_ADMIN")
def delete_policy(policy_id):
    try:
        success = expense_policy_service.delete_policy(policy_id)

        if not success:
            return jsonify({"message": "Expense policy not found"}), 404

        return jsonify({"message": "Expense policy deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# WEB - LIST EXPENSE POLICIES


@expense_policy_bp.route("/expense-policies", methods=["GET"])
@role_required("EMPLOYEE", "MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def web_list_policies():
    page = request.args.get("page", 1, type=int)

    per_page = request.args.get("per_page", 10, type=int)

    policies = expense_policy_service.get_all_policies(page, per_page)

    return render_template(
        "expense_policies/list.html",
        expense_policies=policies
    )

# WEB - ADD EXPENSE POLICY


@expense_policy_bp.route("/expense-policies/add", methods=["GET", "POST"])
@role_required("SYSTEM_ADMIN")
def web_add_policy():
    if request.method == "POST":
        category_id = request.form.get("category_id", "").strip()

        maximum_amount = request.form.get("maximum_amount", "").strip()

        if not category_id:
            flash("Category ID is required", "danger")

            return render_template("expense_policies/add.html")

        if not maximum_amount:
            flash("Maximum amount is required", "danger")

            return render_template("expense_policies/add.html")

        try:
            category_id = int(category_id)
            maximum_amount = float(maximum_amount)

            if maximum_amount <= 0:
                raise ValueError("Maximum amount must be greater than zero")

            expense_policy_service.create_policy(category_id, maximum_amount)

            flash("Expense policy created successfully!", "success")

            return redirect(url_for("expense_policy.web_list_policies"))

        except ValueError as e:
            flash(str(e), "danger")

    return render_template("expense_policies/add.html")

# WEB - DELETE EXPENSE POLICY


@expense_policy_bp.route("/expense-policies/delete/<int:policy_id>", methods=["POST"])
@role_required("SYSTEM_ADMIN")
def web_delete_policy(policy_id):
    try:
        success = expense_policy_service.delete_policy(policy_id)

        if success:
            flash("Expense policy deleted successfully!", "success")

        else:
            flash("Expense policy not found", "danger")

    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("expense_policy.web_list_policies"))

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash

from flask_jwt_extended import get_jwt_identity

from service.user_service import UserService
from dao.users_dao import UserDAO
from dao.employees_dao import EmployeeDAO
from utils.decorators import role_required

user_bp = Blueprint("user", __name__)

user_service = UserService(UserDAO(), EmployeeDAO())

# API - GET ALL USERS


@user_bp.route("/api/users", methods=["GET"])
@role_required("SYSTEM_ADMIN")
def get_users():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    users = user_service.get_all_users(page, per_page)

    return jsonify({
        "users": [user.to_dict() for user in users.items],
        "page": users.page,
        "per_page": users.per_page,
        "total": users.total,
        "pages": users.pages
    }), 200

# API - GET USER BY ID


@user_bp.route("/api/users/<int:user_id>", methods=["GET"])
@role_required("SYSTEM_ADMIN")
def get_user(user_id):
    try:
        user = user_service.get_user(user_id)

        return jsonify({"user": user.to_dict()}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - UPDATE USER


@user_bp.route("/api/users/<int:user_id>", methods=["PUT"])
@role_required("SYSTEM_ADMIN")
def update_user(user_id):
    data = request.get_json()

    email = data.get("email")
    role = data.get("role")

    try:
        user = user_service.update_user(
            user_id,
            email=email,
            role=role
        )

        return jsonify({
            "message": "User updated successfully",
            "user": user.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# API - DELETE USER


@user_bp.route("/api/users/<int:user_id>", methods=["DELETE"])
@role_required("SYSTEM_ADMIN")
def delete_user(user_id):
    try:
        success = user_service.delete_user(user_id)

        if not success:
            return jsonify({"message": "User not found"}), 404

        return jsonify({"message": "User deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# WEB - LIST USERS


@user_bp.route("/users", methods=["GET"])
@role_required("SYSTEM_ADMIN")
def web_list_users():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    users = user_service.get_all_users(page, per_page)

    return render_template(
        "users/list.html",
        users=users
    )

# WEB - DELETE USER


@user_bp.route("/users/delete/<int:user_id>", methods=["POST"])
@role_required("SYSTEM_ADMIN")
def web_delete_user(user_id):
    try:
        success = user_service.delete_user(user_id)

        if success:
            flash("User deleted successfully!", "success")
        else:
            flash("User not found", "danger")

    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("user.web_list_users"))

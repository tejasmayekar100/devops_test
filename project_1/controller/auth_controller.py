from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, make_response

from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required, get_jwt

from service.user_service import UserService
from dao.users_dao import UserDAO
from dao.employees_dao import EmployeeDAO

auth_bp = Blueprint("auth", __name__)

user_service = UserService(UserDAO(), EmployeeDAO())

ALLOWED_ROLES = ["EMPLOYEE", "MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN"]

# API REGISTER


@auth_bp.route("/api/register", methods=["POST"])
def api_register():

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    name = data.get("name")
    department = data.get("department")
    manager_id = data.get("manager_id")

    if not email or not password or not role or not name:
        return jsonify({"message": "Email, password, role and name are required"}), 400

    try:
        user = user_service.register_user(
            email=email,
            password=password,
            role=role,
            name=name,
            department=department,
            manager_id=manager_id
        )

        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# API LOGIN


@auth_bp.route("/api/login", methods=["POST"])
def api_login():

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    try:
        user = user_service.login_user(email, password)

        additional_claims = {
            "role": user.role,
            "email": user.email
        }

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims
        )

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": user.to_dict()
        }), 200

    except ValueError as e:

        return jsonify({"message": str(e)}), 401

# WEB REGISTER


@auth_bp.route("/register", methods=["GET", "POST"])
def web_register():

    if request.method == "POST":
        email = request.form.get("email", "").strip()

        password = request.form.get("password", "").strip()

        role = request.form.get("role", "").upper()

        name = request.form.get("name", "").strip()

        department = request.form.get("department", "").strip()

        manager_id = request.form.get("manager_id", "").strip()

        if not email or not password or not name:
            flash("Name, email and password are required", "danger")

            return render_template(
                "register.html",
                allowed_roles=ALLOWED_ROLES
            )

        if role not in ALLOWED_ROLES:
            flash("Invalid role selected", "danger")

            return render_template(
                "register.html",
                allowed_roles=ALLOWED_ROLES
            )

        if not manager_id:
            manager_id = None

        else:
            try:
                manager_id = int(manager_id)

            except ValueError:
                flash("Manager ID must be a number", "danger")

                return render_template(
                    "register.html",
                    allowed_roles=ALLOWED_ROLES
                )

        try:
            user = user_service.register_user(
                email=email,
                password=password,
                role=role,
                name=name,
                department=department or None,
                manager_id=manager_id
            )

            flash("Registration successful. Please log in.", "success")

            return redirect(url_for("auth.web_login"))

        except ValueError as e:
            flash(str(e), "danger")

            return render_template(
                "register.html",
                allowed_roles=ALLOWED_ROLES
            )

    return render_template(
        "register.html",
        allowed_roles=ALLOWED_ROLES
    )

# WEB LOGIN


@auth_bp.route("/login", methods=["GET", "POST"])
def web_login():

    if request.method == "POST":
        email = request.form.get("email", "").strip()

        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Email and password are required", "danger")

            return render_template("login.html")

        try:
            user = user_service.login_user(email, password)

            additional_claims = {
                "role": user.role,
                "email": user.email
            }

            access_token = create_access_token(
                identity=str(user.id),
                additional_claims=additional_claims
            )

            response = make_response(redirect(url_for("auth.web_home")))

            set_access_cookies(response, access_token)

            flash(f"Welcome back, {user.email}!", "success")

            return response

        except ValueError as e:
            flash(str(e), "danger")

            return render_template("login.html")

    return render_template("login.html")

# WEB HOME


@auth_bp.route("/home", methods=["GET"])
@jwt_required()
def web_home():

    claims = get_jwt()

    return render_template("base.html", current_user=claims)

# WEB LOGOUT


@auth_bp.route("/logout")
def web_logout():
    response = make_response(redirect(url_for("auth.web_login")))

    unset_jwt_cookies(response)

    flash("Logged out successfully", "info")

    return response

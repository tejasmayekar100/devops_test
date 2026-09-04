from flask import Flask, request, jsonify, flash, redirect

from config.database import init_db, db

from flask_jwt_extended import JWTManager

from controller.auth_controller import auth_bp
from controller.user_controller import user_bp
from controller.employee_controller import employee_bp
from controller.travel_request_controller import travel_request_bp
from controller.expense_category_controller import expense_category_bp
from controller.expense_policy_controller import expense_policy_bp
from controller.expense_claim_controller import expense_claim_bp
from controller.approval_controller import approval_bp
from controller.reimbursement_controller import reimbursement_bp

import os
from dotenv import load_dotenv


def create_app():
    load_dotenv()

    app = Flask(__name__)
    init_db(app)

    app.config['SECRET_KEY'] = os.environ["FLASK_SECRET_KEY"]
    app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    # Register all blueprints

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(travel_request_bp)
    app.register_blueprint(expense_category_bp)
    app.register_blueprint(expense_policy_bp)
    app.register_blueprint(expense_claim_bp)
    app.register_blueprint(approval_bp)
    app.register_blueprint(reimbursement_bp)

    # JWT setup

    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def missing_token_callback(err_string):
        # No token was sent at all
        if request.is_json or request.path.startswith("/api"):
            return jsonify({
                "message": "Authorization token is missing",
                "error": "unauthorized"
            }), 401

        flash("Please login first to access this page", "warning")
        return redirect("/login")

    @jwt.invalid_token_loader
    def invalid_token_callback(err_string):
        # Token was sent but is invalid/expired
        if request.is_json or request.path.startswith("/api"):
            return jsonify({
                "message": "Authorization token is invalid",
                "error": "invalid_token"
            }), 401

        flash("Session expired or invalid token, please login again.", "warning")
        return redirect("/login")

    # Create all database tables

    with app.app_context():
        db.create_all()

    # Health check endpoint for Kubernetes
    @app.route("/health")
    def health():
        return jsonify({
            "status": "healthy",
            "version": "v2"
        }), 200

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=3000, debug=False)

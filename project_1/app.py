from flask import Flask, request, jsonify, flash, redirect

from config.database import init_db, db

from flask_jwt_extended import JWTManager

from prometheus_flask_exporter import PrometheusMetrics

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

    # Create Flask application
    app = Flask(__name__)

    # Prometheus Metrics

    metrics = PrometheusMetrics(app)

    metrics.info(
        "flask_app_info",
        "Flask Application Information",
        version="1.0.0"
    )

    # Database setup

    init_db(app)

    # Flask configuration

    app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]
    app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]

    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    # Register Blueprints

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(travel_request_bp)
    app.register_blueprint(expense_category_bp)
    app.register_blueprint(expense_policy_bp)
    app.register_blueprint(expense_claim_bp)
    app.register_blueprint(approval_bp)
    app.register_blueprint(reimbursement_bp)

    # JWT Setup

    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def missing_token_callback(err_string):

        if request.is_json or request.path.startswith("/api"):
            return jsonify({
                "message": "Authorization token is missing",
                "error": "unauthorized"
            }), 401

        flash("Please login first to access this page", "warning")
        return redirect("/login")

    @jwt.invalid_token_loader
    def invalid_token_callback(err_string):

        if request.is_json or request.path.startswith("/api"):
            return jsonify({
                "message": "Authorization token is invalid",
                "error": "invalid_token"
            }), 401

        flash(
            "Session expired or invalid token, please login again",
            "warning"
        )
        return redirect("/login")

    # Health Check

    @app.route("/health")
    def health():
        return jsonify({
            "status": "healthy"
        }), 200

    # Create Database Tables

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()

    app.run(
        host="0.0.0.0",
        port=3000,
        debug=False
    )

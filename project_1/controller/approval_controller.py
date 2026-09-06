from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash

from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from service.approval_service import ApprovalService

from dao.approval_history_dao import ApprovalHistoryDAO
from dao.expense_claims_dao import ExpenseClaimDAO
from dao.employees_dao import EmployeeDAO

from utils.decorators import role_required

approval_bp = Blueprint("approval", __name__)

approval_service = ApprovalService(
    ApprovalHistoryDAO(),
    ExpenseClaimDAO(),
    EmployeeDAO()
)

# API - GET ALL APPROVAL HISTORY


@approval_bp.route("/api/approvals", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_approval_history():
    page = request.args.get("page", 1, type=int)

    per_page = request.args.get("per_page", 10, type=int)

    approvals = approval_service.get_all_approval_history(page, per_page)

    return jsonify({
        "approval_history": [approval.to_dict() for approval in approvals.items],
        "page": approvals.page,
        "per_page": approvals.per_page,
        "total": approvals.total,
        "pages": approvals.pages
    }), 200

# API - GET APPROVAL RECORD BY ID


@approval_bp.route("/api/approvals/<int:approval_id>", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_approval(approval_id):
    try:
        approval = approval_service.get_approval_history(approval_id)

        return jsonify({"approval": approval.to_dict()}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404

# API - GET APPROVAL HISTORY FOR AN EXPENSE CLAIM


@approval_bp.route("/api/expense-claims/<int:claim_id>/approvals", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def get_claim_approval_history(claim_id):
    approvals = approval_service.get_claim_history(claim_id)

    return jsonify({"approval_history": [approval.to_dict() for approval in approvals]}), 200

# API - APPROVE EXPENSE CLAIM


@approval_bp.route("/api/expense-claims/<int:claim_id>/approve", methods=["PATCH"])
@role_required("MANAGER")
def approve_claim(claim_id):
    user_id = int(get_jwt_identity())

    data = request.get_json(silent=True) or {}

    comment = data.get("comment")

    # Keep comment within the model's VARCHAR(255) limit.
    if comment is not None:
        comment = str(comment).strip()
        if len(comment) > 255:
            return jsonify({"message": "Comment cannot exceed 255 characters"}), 400

        if not comment:
            comment = None

    try:
        approval = approval_service.approve_claim(
            claim_id=claim_id,
            user_id=user_id,
            comment=comment
        )

        return jsonify({
            "message": "Expense claim approved successfully",
            "approval": approval.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# API - REJECT EXPENSE CLAIM


@approval_bp.route("/api/expense-claims/<int:claim_id>/reject", methods=["PATCH"])
@role_required("MANAGER")
def reject_claim(claim_id):
    user_id = int(get_jwt_identity())

    data = request.get_json(silent=True) or {}

    comment = data.get("comment")

    # Keep comment within the model's VARCHAR(255) limit.
    if comment is not None:
        comment = str(comment).strip()
        if len(comment) > 255:
            return jsonify({"message": "Comment cannot exceed 255 characters"}), 400

        if not comment:
            comment = None

    try:
        approval = approval_service.reject_claim(
            claim_id=claim_id,
            user_id=user_id,
            comment=comment
        )

        return jsonify({
            "message": "Expense claim rejected successfully",
            "approval": approval.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# WEB - LIST APPROVAL HISTORY


@approval_bp.route("/approvals", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def web_list_approvals():
    page = request.args.get("page", 1, type=int)

    per_page = request.args.get("per_page", 10, type=int)

    approvals = approval_service.get_all_approval_history(page, per_page)

    return render_template(
        "approvals/list.html",
        approvals=approvals
    )

# WEB - VIEW APPROVAL RECORD


@approval_bp.route("/approvals/<int:approval_id>", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def web_view_approval(approval_id):
    try:
        approval = approval_service.get_approval_history(approval_id)

        return render_template(
            "approvals/detail.html",
            approval=approval
        )

    except ValueError as e:
        flash(str(e), "danger")

        return redirect(url_for("approval.web_list_approvals"))

# WEB - VIEW CLAIM APPROVAL HISTORY


@approval_bp.route("/expense-claims/<int:claim_id>/approvals", methods=["GET"])
@role_required("MANAGER", "FINANCE_ADMIN", "SYSTEM_ADMIN")
def web_claim_approval_history(claim_id):
    approvals = approval_service.get_claim_history(claim_id)

    return render_template(
        "approvals/claim_history.html",
        claim_id=claim_id,
        approvals=approvals,
        current_user=get_jwt()
    )

# WEB - APPROVE EXPENSE CLAIM


@approval_bp.route("/expense-claims/<int:claim_id>/approve", methods=["POST"])
@role_required("MANAGER")
def web_approve_claim(claim_id):
    user_id = int(get_jwt_identity())

    comment = request.form.get("comment", "").strip()

    if len(comment) > 255:
        flash("Comment cannot exceed 255 characters", "danger")

        return redirect(url_for("approval.web_claim_approval_history", claim_id=claim_id))

    try:
        approval_service.approve_claim(
            claim_id=claim_id,
            user_id=user_id,
            comment=comment or None
        )

        flash("Expense claim approved successfully!", "success")

    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("approval.web_claim_approval_history", claim_id=claim_id))

# WEB - REJECT EXPENSE CLAIM


@approval_bp.route("/expense-claims/<int:claim_id>/reject", methods=["POST"])
@role_required("MANAGER")
def web_reject_claim(claim_id):
    user_id = int(get_jwt_identity())

    comment = request.form.get("comment", "").strip()

    if len(comment) > 255:
        flash("Comment cannot exceed 255 characters", "danger")

        return redirect(url_for("approval.web_claim_approval_history", claim_id=claim_id))

    try:
        approval_service.reject_claim(
            claim_id=claim_id,
            user_id=user_id,
            comment=comment or None
        )

        flash("Expense claim rejected successfully!", "success")

    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("approval.web_claim_approval_history", claim_id=claim_id))

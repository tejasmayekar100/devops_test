from functools import wraps

from flask import request, jsonify, render_template

from flask_jwt_extended import jwt_required, get_jwt


def role_required(*roles):

    def decorator(function):
        @wraps(function)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()

            user_role = claims.get("role")

            if user_role not in roles:
                # API request
                if (request.is_json or request.path.startswith("/api")):
                    return jsonify({"message": "Forbidden"}), 403

                # Browser/web request
                return render_template(
                    "403.html",
                    error="Forbidden: You do not have permission to access this page"
                ), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator

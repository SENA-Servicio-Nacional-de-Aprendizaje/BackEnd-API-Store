# src/middlewares/authorization.py
"""Middleware de autorizacion por roles (equivalente a middlewares/authorization.middleware.js)."""

from functools import wraps

from flask import jsonify, request


def authorization_user(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            try:
                role = request.payload.get("role")

                if not role:
                    return jsonify({"msg": "No tiene los permisos definidos"}), 404

                if role not in allowed_roles:
                    return jsonify({
                        "msg": f"El rol {role} no esta autorizado para esta acción"
                    }), 403

                print(f"El rol {role} está autorizado para esta acción")

                return view_func(*args, **kwargs)
            except Exception as error:
                print(error)
                return jsonify({"msg": "Error de autorización del servidor"}), 500

        return wrapper

    return decorator

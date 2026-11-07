# src/middlewares/authentication.py
"""Middleware de autenticacion JWT (equivalente a middlewares/authentication.middleware.js)."""

from functools import wraps

from flask import g, jsonify, request

from src.helpers.jwt_helper import verify_token
from src.helpers.serializer import to_serializable
from src.services.user_services import db_get_user_by_email


def authentication_user(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # Paso 1: Obtener la cadena que contiene el Token
        token = request.headers.get("X-Token")

        if not token:
            return jsonify({"msg": "Cadena de Token vacia"}), 401

        # Paso 2: Verificar formato del Token
        token_parts = token.split(".")

        if len(token_parts) != 3:
            return jsonify({"msg": "Formato del token invalido"}), 400

        # Paso 3: Verificar autenticidad y extraer payload
        payload = verify_token(token)

        if not payload:
            return jsonify({"msg": "Token invalido o inactivo"}), 400

        # Paso 4: Verificar que el usuario del payload existe y sigue activo
        user_found = db_get_user_by_email(payload.get("email"))

        if not user_found:
            return jsonify({"msg": "No es posible generar el nuevo Token"}), 400

        # Paso 5: Eliminar propiedades innecesarias
        user_found_obj = to_serializable(user_found)
        user_found_obj.pop("password", None)
        user_found_obj.pop("createdAt", None)
        user_found_obj.pop("updatedAt", None)

        # Paso 6: Almacenar datos para la siguiente funcion
        request.payload = user_found_obj
        request.user = user_found

        # Paso 7: Dar paso a la siguiente funcion
        return view_func(*args, **kwargs)

    return wrapper

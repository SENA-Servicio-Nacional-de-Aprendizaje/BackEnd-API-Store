# src/controllers/auth_controller.py
"""Controlador de Autenticacion (equivalente a controllers/auth.controller.js)."""

from flask import jsonify, request

from src.helpers.bcrypt_helper import validate_password
from src.helpers.jwt_helper import generate_token
from src.helpers.request_helper import get_input_data
from src.helpers.serializer import to_serializable
from src.services.user_services import db_get_user_by_email


def login_user():
    try:
        input_data = get_input_data()

        if not input_data.get("password"):
            raise ValueError("Se olvidó pasar la propiedad password en el login")

        # Verificar si el usuario existe
        user_found = db_get_user_by_email(input_data.get("email"))

        if not user_found:
            raise ValueError("El usuario no existe, por favor registrese")

        # Verificar contrasena
        is_valid = validate_password(input_data.get("password"), user_found.password)

        if not is_valid:
            raise ValueError("Sus credenciales no son validas")

        # Generar token
        payload = {
            "_id": str(user_found.id),
            "name": user_found.name,
            "nickname": user_found.nickname,
            "email": user_found.email,
            "role": user_found.role,
            "avatar": user_found.avatarUrl,
            "status": user_found.status,
        }

        token = generate_token(payload)

        if token is None:
            raise RuntimeError("No se pudo generar el token de acceso")

        user_found_obj = to_serializable(user_found)
        user_found_obj.pop("password", None)

        return jsonify({
            "msg": "Login exitoso",
            "token": token,
            "data": user_found_obj,
        })

    except ValueError as error:
        msg = str(error)
        if "Se olvidó pasar" in msg or "El usuario no existe" in msg or "Sus credenciales no son validas" in msg:
            return jsonify({"msg": msg}), 400
        return jsonify({"msg": "Ocurrió un error en el servidor durante el login"}), 500
    except RuntimeError as error:
        if "No se pudo generar el token de acceso" in str(error):
            return jsonify({"msg": str(error)}), 500
        return jsonify({"msg": "Ocurrió un error en el servidor durante el login"}), 500
    except Exception as error:
        print(error)
        return jsonify({"msg": "Ocurrió un error en el servidor durante el login"}), 500


def re_new_token():
    payload = request.payload
    user = request.user

    user_found = db_get_user_by_email(payload.get("email"))

    if not user_found:
        return jsonify({
            "msg": "No se renueva el Token, porque el usuario a sido eliminado o su estado es inactivo"
        }), 400

    new_payload = {
        "_id": str(user_found.id),
        "name": user_found.name,
        "nickname": user_found.nickname,
        "email": user_found.email,
        "role": user_found.role,
        "avatar": user_found.avatarUrl,
        "status": user_found.status,
    }

    token = generate_token(new_payload)

    user_found_obj = to_serializable(user_found)
    user_found_obj.pop("createdAt", None)
    user_found_obj.pop("password", None)
    user_found_obj.pop("updatedAt", None)

    return jsonify({
        "msg": "Aqui se renueva el Token",
        "token": token,
        "data": user_found_obj,
    })

# src/controllers/user_controller.py
"""Controlador de Usuario (equivalente a controllers/user.controller.js)."""

from flask import jsonify, request
from sqlalchemy.exc import IntegrityError

from src.helpers.bcrypt_helper import encrypted_password
from src.helpers.file_storage import delete_old_image
from src.helpers.request_helper import get_input_data
from src.helpers.serializer import to_serializable
from src.middlewares.upload import handle_upload_avatar as upload_avatar_decorator  # noqa: F401
from src.services.user_services import (
    db_create_user,
    db_delete_user,
    db_get_user_by_email,
    db_get_user_by_id_raw,
    db_get_user_by_nickname,
    db_get_users,
    db_update_user,
)


def get_users():
    try:
        users = db_get_users()

        if len(users) == 0:
            raise ValueError("No se encontraron usuarios registrados en el sistema")

        return jsonify({
            "msg": "Lista de todos los usuarios",
            "data": [to_serializable(u) for u in users],
        })
    except ValueError as error:
        if "No se encontraron usuarios registrados" in str(error):
            return jsonify({"msg": str(error)}), 404
        return jsonify({"msg": "No se pudo obtener la lista de usuarios"}), 500
    except Exception as error:
        print(error)
        return jsonify({"msg": "No se pudo obtener la lista de usuarios"}), 500


def get_user_by_id(id):
    try:
        existing_user = db_get_user_by_id_raw(id)

        if not existing_user:
            raise ValueError("El usuario solicitado no existe en el sistema")

        return jsonify({"data": to_serializable(existing_user)})
    except ValueError as error:
        if "El usuario solicitado no existe" in str(error):
            return jsonify({"msg": str(error)}), 404
        return jsonify({"msg": "No se pudo obtener el usuario"}), 500
    except Exception as error:
        print(error)
        return jsonify({"msg": "No se pudo obtener el usuario"}), 500


def create_user():
    try:
        input_data = get_input_data()

        # Si se subio un archivo, asignar su ruta a avatarUrl
        uploaded_avatar = getattr(request, "uploaded_avatar", None)
        if uploaded_avatar:
            input_data["avatarUrl"] = uploaded_avatar

        if isinstance(input_data.get("status"), str):
            input_data["status"] = input_data["status"].lower() == "true"

        if not input_data.get("password"):
            raise ValueError("Se olvidó pasar la propiedad password")

        input_data["password"] = encrypted_password(input_data["password"])

        data = db_create_user(input_data)

        return jsonify({
            "msg": "Registra el usuario de forma publica exitosamente",
            "data": to_serializable(data),
        }), 201
    except ValueError as error:
        if "Se olvidó pasar la propiedad password" in str(error):
            return jsonify({"msg": str(error)}), 400
        return jsonify({"msg": "No se pudo registrar el usuario"}), 500
    except IntegrityError:
        # Eliminar imagen subida si fallo
        uploaded_avatar = getattr(request, "uploaded_avatar", None)
        if uploaded_avatar:
            delete_old_image(uploaded_avatar)

        duplicated_field = None
        if input_data.get("email") and db_get_user_by_email(input_data.get("email")):
            duplicated_field = "email"
        elif input_data.get("nickname") and db_get_user_by_nickname(input_data.get("nickname")):
            duplicated_field = "nickname"

        error_messages = {
            "email": "El correo electrónico ya se encuentra registrado por otro usuario",
            "nickname": "El nickname ya se encuentra en uso por otro usuario",
        }
        return jsonify({
            "msg": error_messages.get(duplicated_field, "Ya existe un registro con algunos de estos valores únicos")
        }), 400
    except Exception as error:
        print(error)
        return jsonify({"msg": "No se pudo registrar el usuario"}), 500


def update_user(id):
    try:
        input_data = get_input_data()
        email = input_data.get("email")
        nickname = input_data.get("nickname")

        existing_user = db_get_user_by_id_raw(id)

        if not existing_user:
            raise ValueError("El usuario que deseas actualizar no existe en el sistema")

        uploaded_avatar = getattr(request, "uploaded_avatar", None)
        if uploaded_avatar:
            delete_old_image(existing_user.avatarUrl)
            input_data["avatarUrl"] = uploaded_avatar
        elif input_data.get("avatarUrl") == "":
            delete_old_image(existing_user.avatarUrl)
            input_data["avatarUrl"] = "uploads/avatars/default-avatar.png"

        data = db_update_user(id, input_data)

        return jsonify({"data": to_serializable(data)})
    except ValueError as error:
        if "El usuario que deseas actualizar no existe" in str(error):
            return jsonify({"msg": str(error)}), 404
        return jsonify({"msg": "No se pudo actualizar el usuario"}), 500
    except Exception as error:
        print(error)
        return jsonify({"msg": "No se pudo actualizar el usuario"}), 500


def delete_user(id):
    try:
        user = db_get_user_by_id_raw(id)

        if not user:
            return jsonify({"msg": "Usuario no encontrado"}), 404

        delete_old_image(user.avatarUrl)

        data = db_delete_user(id)

        return jsonify({
            "msg": "Usuario eliminado exitosamente",
            "data": to_serializable(data),
        })
    except Exception as error:
        print(error)
        return jsonify({"msg": "No se pudo eliminar el usuario"}), 500

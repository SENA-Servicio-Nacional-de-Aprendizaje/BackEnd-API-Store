# src/services/user_services.py
"""Servicio de Usuario (equivalente a services/user.services.js)."""

from bson import ObjectId

from src.models.user_model import User


def _to_object_id(value):
    try:
        return ObjectId(value)
    except Exception:
        return value


def db_get_users():
    """Obtiene todos los usuarios activos."""
    return list(User.objects(status=True))


def db_get_user_by_id(id):
    """Obtiene un usuario activo por su ID."""
    try:
        return User.objects(id=id, status=True).first()
    except Exception:
        return None


def db_get_user_by_id_raw(id):
    """Obtiene un usuario por su ID sin filtrar por status."""
    try:
        return User.objects(id=id).first()
    except Exception:
        return None


def db_get_user_by_email(email):
    """Obtiene un usuario activo por su email."""
    if not email:
        raise ValueError("Se olvidó pasar la propiedad email en el login")
    return User.objects(email=str(email).lower(), status=True).first()


def db_get_user_by_nickname(nickname):
    """Obtiene un usuario por su nickname."""
    return User.objects(nickname=str(nickname).lower()).first()


def db_create_user(new_user):
    """Registra un nuevo usuario en la base de datos."""
    # Normalizar email y nickname a minusculas
    if "email" in new_user and new_user["email"]:
        new_user["email"] = str(new_user["email"]).lower()
    if "nickname" in new_user and new_user["nickname"]:
        new_user["nickname"] = str(new_user["nickname"]).lower()

    user = User(**new_user)
    user.save()
    return user


def db_update_user(id, update_data):
    """Actualiza un usuario por su ID."""
    if isinstance(update_data, dict):
        # Normalizar campos unicos
        if "email" in update_data and update_data["email"]:
            update_data["email"] = str(update_data["email"]).lower()
        if "nickname" in update_data and update_data["nickname"]:
            update_data["nickname"] = str(update_data["nickname"]).lower()

    try:
        user = User.objects(id=id).first()
    except Exception:
        return None
    if not user:
        return None

    for key, value in (update_data or {}).items():
        if hasattr(user, key):
            setattr(user, key, value)
    user.save()
    return user


def db_delete_user(id):
    """Elimina un usuario por su ID."""
    try:
        user = User.objects(id=id).first()
    except Exception:
        return None
    if not user:
        return None
    user.delete()
    return user

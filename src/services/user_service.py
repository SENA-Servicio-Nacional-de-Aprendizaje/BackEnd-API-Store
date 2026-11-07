# src/services/user_service.py
"""Servicio de Usuario (equivalente a services/user.services.js)."""

from src.db.database import SessionLocal
from src.models.user_model import User


def db_get_users():
    """Obtiene todos los usuarios activos."""
    db = SessionLocal()
    try:
        return list(db.query(User).filter(User.status == True).all())
    finally:
        db.close()


def db_get_user_by_id(id):
    """Obtiene un usuario activo por su ID."""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == int(id), User.status == True).first()
    except Exception:
        return None
    finally:
        db.close()


def db_get_user_by_id_raw(id):
    """Obtiene un usuario por su ID sin filtrar por status."""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == int(id)).first()
    except Exception:
        return None
    finally:
        db.close()


def db_get_user_by_email(email):
    """Obtiene un usuario activo por su email."""
    if not email:
        raise ValueError("Se olvidó pasar la propiedad email en el login")
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == str(email).lower(), User.status == True).first()
    finally:
        db.close()


def db_get_user_by_nickname(nickname):
    """Obtiene un usuario por su nickname."""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.nickname == str(nickname).lower()).first()
    finally:
        db.close()


def db_create_user(new_user):
    """Registra un nuevo usuario en la base de datos."""
    # Normalizar email y nickname a minusculas
    if "email" in new_user and new_user["email"]:
        new_user["email"] = str(new_user["email"]).lower()
    if "nickname" in new_user and new_user["nickname"]:
        new_user["nickname"] = str(new_user["nickname"]).lower()

    db = SessionLocal()
    try:
        user = User(**new_user)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def db_update_user(id, update_data):
    """Actualiza un usuario por su ID."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(id)).first()
        if not user:
            return None

        if isinstance(update_data, dict):
            # Normalizar campos unicos
            if "email" in update_data and update_data["email"]:
                update_data["email"] = str(update_data["email"]).lower()
            if "nickname" in update_data and update_data["nickname"]:
                update_data["nickname"] = str(update_data["nickname"]).lower()

        for key, value in (update_data or {}).items():
            if hasattr(user, key):
                setattr(user, key, value)

        db.commit()
        return user
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()


def db_delete_user(id):
    """Elimina un usuario por su ID."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(id)).first()
        if not user:
            return None
        db.delete(user)
        db.commit()
        return user
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()

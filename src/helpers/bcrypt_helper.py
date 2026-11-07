# src/helpers/bcrypt_helper.py
"""Utilidades para encriptar y validar contrasenas (equivalente a helpers/bcrypt.helper.js)."""

import bcrypt


def encrypted_password(original_password):
    """Encripta una contrasena usando bcrypt (cost factor 4, como en Node)."""
    try:
        salt = bcrypt.gensalt(rounds=4)
        hash_password = bcrypt.hashpw(original_password.encode("utf-8"), salt)
        return hash_password.decode("utf-8")
    except Exception as error:
        print(error)
        return None


def validate_password(original_password, hash_password):
    """Valida una contrasena en texto plano contra su hash bcrypt."""
    try:
        return bcrypt.checkpw(
            original_password.encode("utf-8"),
            hash_password.encode("utf-8")
        )
    except Exception as error:
        print(error)
        return None

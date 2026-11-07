# src/helpers/jwt_helper.py
"""Utilidades para generar y verificar JSON Web Tokens (equivalente a helpers/jwt.helper.js)."""

import os
import datetime

import jwt

JWT_SEED = os.getenv("JWT_SEED") or "123456789ABCabc"


def generate_token(payload):
    """Genera un JWT con expiracion de 1 hora."""
    try:
        # Copiamos el payload para no mutar el original
        data = dict(payload)
        data["exp"] = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        token = jwt.encode(data, JWT_SEED, algorithm="HS256")
        return token
    except Exception as error:
        print(error)
        return None


def verify_token(token):
    """Verifica y decodifica un JWT. Retorna el payload o None si es invalido."""
    try:
        payload = jwt.decode(token, JWT_SEED, algorithms=["HS256"])
        return payload
    except Exception as error:
        print(error)
        return None

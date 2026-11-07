# src/services/role_service.py
"""Servicio de Roles (equivalente a services/role.service.js)."""

from src.config.global_config import ALLOWED_ROLES, ROLE_LABELS


def db_get_roles():
    """Retorna la lista de roles con su etiqueta legible."""
    return [
        {"id": role, "name": ROLE_LABELS.get(role, role)}
        for role in ALLOWED_ROLES
    ]

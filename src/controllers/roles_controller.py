# src/controllers/roles_controller.py
"""Controlador de Roles (equivalente a controllers/roles.controller.js)."""

from flask import jsonify

from src.services.role_service import db_get_roles


def get_roles():
    roles = db_get_roles()
    return jsonify({
        "msg": "Obtiene todos los roles definidos para la aplcacion",
        "data": roles,
    })

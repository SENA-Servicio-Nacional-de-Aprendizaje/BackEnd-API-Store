# src/routes/roles_routes.py
"""Rutas de roles (equivalente a routes/roles.routes.js)."""

from flask import Blueprint

from src.controllers.roles_controller import get_roles

roles_bp = Blueprint("roles", __name__)

roles_bp.route("/", methods=["GET"])(get_roles)

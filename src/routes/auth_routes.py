# src/routes/auth_routes.py
"""Rutas de autenticacion (equivalente a routes/auth.routes.js)."""

from flask import Blueprint

from src.controllers.auth_controller import login_user, re_new_token
from src.controllers.user_controller import create_user
from src.middlewares.authentication import authentication_user
from src.middlewares.without_role import remove_role

auth_bp = Blueprint("auth", __name__)

# http://localhost:3000/api/auth
auth_bp.route("/login", methods=["POST"])(login_user)
auth_bp.route("/register", methods=["POST"])(remove_role(create_user))
auth_bp.route("/renew-token", methods=["GET"])(authentication_user(re_new_token))

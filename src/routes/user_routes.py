# src/routes/user_routes.py
"""Rutas de usuario (equivalente a routes/user.routes.js)."""

from flask import Blueprint

from src.config.global_config import ROLES
from src.controllers.user_controller import (
    create_user,
    delete_user,
    get_user_by_id,
    get_users,
    update_user,
)
from src.middlewares.authentication import authentication_user
from src.middlewares.authorization import authorization_user
from src.middlewares.upload import handle_upload_avatar

user_bp = Blueprint("users", __name__)

user_bp.route(
    "/", methods=["GET"]
)(authentication_user(authorization_user([ROLES["SUPER_ADMIN"], ROLES["ADMIN"]])(get_users)))

user_bp.route(
    "/", methods=["POST"]
)(authentication_user(authorization_user([ROLES["SUPER_ADMIN"], ROLES["ADMIN"]])(
    handle_upload_avatar(create_user)
)))

user_bp.route(
    "/<id>", methods=["GET"]
)(authentication_user(authorization_user([ROLES["SUPER_ADMIN"], ROLES["ADMIN"]])(
    get_user_by_id
)))

user_bp.route(
    "/<id>", methods=["PATCH"]
)(authentication_user(authorization_user([ROLES["SUPER_ADMIN"], ROLES["ADMIN"]])(
    handle_upload_avatar(update_user)
)))

user_bp.route(
    "/<id>", methods=["DELETE"]
)(authentication_user(authorization_user([ROLES["SUPER_ADMIN"], ROLES["ADMIN"]])(
    delete_user
)))

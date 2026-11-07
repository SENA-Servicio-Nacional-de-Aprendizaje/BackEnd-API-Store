# src/routes/category_routes.py
"""Rutas de categoria (equivalente a routes/category.routes.js)."""

from flask import Blueprint

from src.config.global_config import ROLES
from src.controllers.category_controller import (
    create_category,
    delete_category,
    get_categories,
    get_category_by_id,
    update_category,
)
from src.middlewares.authentication import authentication_user
from src.middlewares.authorization import authorization_user
from src.middlewares.upload import handle_upload_category_image

category_bp = Blueprint("categories", __name__)

# Consultas publicas
category_bp.route("/", methods=["GET"])(get_categories)
category_bp.route("/<id>", methods=["GET"])(get_category_by_id)

# Operaciones protegidas
category_bp.route(
    "/", methods=["POST"]
)(authentication_user(authorization_user([ROLES["SUPER_ADMIN"], ROLES["ADMIN"], ROLES["EDITOR"]])(
    handle_upload_category_image(create_category)
)))

category_bp.route(
    "/<id>", methods=["PATCH"]
)(authentication_user(authorization_user([ROLES["SUPER_ADMIN"], ROLES["ADMIN"], ROLES["EDITOR"]])(
    handle_upload_category_image(update_category)
)))

category_bp.route(
    "/<id>", methods=["DELETE"]
)(authentication_user(authorization_user([ROLES["SUPER_ADMIN"], ROLES["ADMIN"]])(
    delete_category
)))

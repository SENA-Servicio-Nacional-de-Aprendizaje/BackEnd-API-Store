# src/routes/product_routes.py
"""Rutas de producto (equivalente a routes/product.routes.js)."""

from flask import Blueprint

from src.config.global_config import ROLES
from src.controllers.product_controller import (
    create_product,
    delete_product,
    get_product_by_id,
    get_products,
    update_product,
)
from src.middlewares.authentication import authentication_user
from src.middlewares.authorization import authorization_user
from src.middlewares.upload import handle_upload_product_images

product_bp = Blueprint("products", __name__)

# Consultas publicas
product_bp.route("/", methods=["GET"])(get_products)
product_bp.route("/<id>", methods=["GET"])(get_product_by_id)

# Operaciones protegidas
product_bp.route(
    "/", methods=["POST"]
)(authentication_user(authorization_user([ROLES["SUPER_ADMIN"], ROLES["ADMIN"], ROLES["EDITOR"]])(
    handle_upload_product_images(create_product)
)))

product_bp.route(
    "/<id>", methods=["PATCH"]
)(authentication_user(authorization_user([ROLES["SUPER_ADMIN"], ROLES["ADMIN"], ROLES["EDITOR"]])(
    handle_upload_product_images(update_product)
)))

product_bp.route(
    "/<id>", methods=["DELETE"]
)(authentication_user(authorization_user([ROLES["SUPER_ADMIN"], ROLES["ADMIN"]])(
    delete_product
)))

# src/routes/cart_routes.py
"""Rutas de carrito (equivalente a routes/cart.routes.js)."""

from flask import Blueprint

from src.controllers.cart_controller import (
    clear_cart,
    get_cart,
    remove_item_from_cart,
    sync_cart,
    update_cart,
)
from src.middlewares.authentication import authentication_user

cart_bp = Blueprint("cart", __name__)

cart_bp.route("/", methods=["GET"])(authentication_user(get_cart))
cart_bp.route("/", methods=["PUT"])(authentication_user(update_cart))
cart_bp.route("/sync", methods=["POST"])(authentication_user(sync_cart))
cart_bp.route("/item/<product_id>", methods=["DELETE"])(authentication_user(remove_item_from_cart))
cart_bp.route("/", methods=["DELETE"])(authentication_user(clear_cart))

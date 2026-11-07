# src/routes/order_routes.py
"""Rutas de ordenes (equivalente a routes/order.routes.js)."""

from flask import Blueprint

from src.controllers.order_controller import create_order, get_order_by_id, get_user_orders
from src.middlewares.authentication import authentication_user

order_bp = Blueprint("orders", __name__)

order_bp.route("/", methods=["POST"])(authentication_user(create_order))
order_bp.route("/", methods=["GET"])(authentication_user(get_user_orders))
order_bp.route("/<id>", methods=["GET"])(authentication_user(get_order_by_id))


# src/routes/roles_routes.py
"""Rutas de roles (equivalente a routes/roles.routes.js)."""

from flask import Blueprint

from src.controllers.roles_controller import get_roles

roles_bp = Blueprint("roles", __name__)

roles_bp.route("/", methods=["GET"])(get_roles)

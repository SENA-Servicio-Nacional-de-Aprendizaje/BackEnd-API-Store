# src/controllers/order_controller.py
"""Controlador de Ordenes (equivalente a controllers/order.controller.js)."""

from flask import jsonify, request

from src.helpers.serializer import to_serializable
from src.helpers.request_helper import get_input_data
from src.services.order_service import db_create_order, db_get_order_by_id, db_get_orders_by_user_id


def _user_id():
    user = request.user
    return str(user.id) if hasattr(user, "id") else str(user)


def create_order():
    try:
        user_id = _user_id()
        input_data = get_input_data()
        shipping_address = input_data.get("shippingAddress")

        if not shipping_address or not shipping_address.get("address") or not shipping_address.get("city") or not shipping_address.get("phone"):
            return jsonify({"msg": "La dirección de envío (dirección, ciudad y teléfono) es obligatoria"}), 400

        new_order = db_create_order(user_id, input_data)

        return jsonify({"msg": "Orden de compra creada exitosamente", "data": to_serializable(new_order)}), 201
    except Exception as error:
        print("Error al crear la orden:", error)
        return jsonify({"msg": str(error) or "Error al procesar la orden de compra"}), 400


def get_user_orders():
    try:
        user_id = _user_id()
        orders = db_get_orders_by_user_id(user_id)
        return jsonify({"msg": "Historial de órdenes obtenido con éxito", "data": [to_serializable(o) for o in orders]})
    except Exception as error:
        print("Error al obtener órdenes:", error)
        return jsonify({"msg": "Error interno del servidor al obtener las órdenes"}), 500


def get_order_by_id(id):
    try:
        user_id = _user_id()
        order = db_get_order_by_id(id, user_id)

        if not order:
            return jsonify({"msg": "Orden no encontrada o no pertenece al usuario"}), 404

        return jsonify({"msg": "Detalle de la orden obtenido con éxito", "data": to_serializable(order)})
    except Exception as error:
        print("Error al obtener la orden por ID:", error)
        return jsonify({"msg": "Error interno del servidor al obtener el detalle de la orden"}), 500

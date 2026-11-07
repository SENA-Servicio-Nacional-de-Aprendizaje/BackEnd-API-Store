# src/controllers/cart_controller.py
"""Controlador de Carrito (equivalente a controllers/cart.controller.js)."""

from flask import jsonify, request

from src.helpers.serializer import to_serializable
from src.helpers.request_helper import get_input_data
from src.services.cart_service import (
    db_clear_cart,
    db_get_cart_by_user_id,
    db_remove_item_from_cart,
    db_sync_cart,
    db_update_cart,
)


def _user_id():
    user = request.user
    return str(user.id) if hasattr(user, "id") else str(user["_id"] if isinstance(user, dict) else user)


def get_cart():
    try:
        user_id = _user_id()
        cart = db_get_cart_by_user_id(user_id)
        return jsonify({"msg": "Carrito obtenido con éxito", "data": to_serializable(cart)})
    except Exception as error:
        print("Error al obtener el carrito:", error)
        return jsonify({"msg": "Error interno del servidor al obtener el carrito"}), 500


def update_cart():
    try:
        user_id = _user_id()
        input_data = get_input_data()
        items = input_data.get("items")

        if not isinstance(items, list):
            return jsonify({"msg": "El cuerpo de la petición debe contener un arreglo de ítems válido"}), 400

        cart = db_update_cart(user_id, items)
        return jsonify({"msg": "Carrito actualizado con éxito", "data": to_serializable(cart)})
    except Exception as error:
        print("Error al actualizar el carrito:", error)
        return jsonify({"msg": "Error interno del servidor al actualizar el carrito"}), 500


def sync_cart():
    try:
        user_id = _user_id()
        input_data = get_input_data()
        items = input_data.get("items")
        guest_items = items if isinstance(items, list) else []

        cart = db_sync_cart(user_id, guest_items)
        return jsonify({"msg": "Carrito sincronizado con éxito", "data": to_serializable(cart)})
    except Exception as error:
        print("Error al sincronizar el carrito:", error)
        return jsonify({"msg": "Error interno del servidor al sincronizar el carrito"}), 500


def remove_item_from_cart(product_id):
    try:
        user_id = _user_id()
        cart = db_remove_item_from_cart(user_id, product_id)
        return jsonify({"msg": "Producto eliminado del carrito con éxito", "data": to_serializable(cart)})
    except Exception as error:
        print("Error al eliminar producto del carrito:", error)
        return jsonify({"msg": "Error interno del servidor al eliminar el producto"}), 500


def clear_cart():
    try:
        user_id = _user_id()
        cart = db_clear_cart(user_id)
        return jsonify({"msg": "Carrito vaciado con éxito", "data": to_serializable(cart)})
    except Exception as error:
        print("Error al vaciar el carrito:", error)
        return jsonify({"msg": "Error interno del servidor al vaciar el carrito"}), 500

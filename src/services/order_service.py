# src/services/order_service.py
"""Servicio de Ordenes (equivalente a services/order.service.js)."""

import random
import time
from datetime import datetime, timezone

from src.db.database import SessionLocal
from src.models.cart_model import Cart
from src.models.order_model import Order, OrderItem, ShippingAddress
from src.models.product_model import Product


def _extract_product_id(value):
    if isinstance(value, dict):
        return value.get("_id") or value.get("id") or value.get("product")
    if hasattr(value, "id"):
        return value.id
    return value


def _to_number(value):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def _get_cart_items(user_id):
    """Obtiene los items del carrito del usuario autenticado."""
    db = SessionLocal()
    try:
        cart = db.query(Cart).filter(Cart.user_id == int(user_id)).first()
        if not cart or not cart.items or len(cart.items) == 0:
            return []
        return [
            {"product": item.product_id, "quantity": item.quantity}
            for item in cart.items
        ]
    finally:
        db.close()


def db_create_order(user_id, order_payload):
    """Crea una nueva orden de compra."""
    shipping_address = order_payload.get("shippingAddress") or {}
    payment_method = order_payload.get("paymentMethod")
    direct_items = order_payload.get("items")

    items_to_process = []
    if isinstance(direct_items, list) and len(direct_items) > 0:
        items_to_process = direct_items
    else:
        items_to_process = _get_cart_items(user_id)
        if len(items_to_process) == 0:
            raise Exception("El carrito de compras está vacío")

    db = SessionLocal()
    try:
        order_items = []
        calculated_total = 0.0
        products_to_update = []

        for item in items_to_process:
            product_id = _extract_product_id(item.get("product"))
            requested_qty = _to_number(item.get("quantity"))

            if not product_id or requested_qty <= 0:
                continue

            product = db.query(Product).filter(Product.id == int(product_id)).first()
            if not product or not product.status:
                raise Exception("El producto no está disponible en la tienda")

            if product.stock < requested_qty:
                raise Exception(
                    f'Stock insuficiente para "{product.name}". Disponible: {product.stock}, Solicitado: {requested_qty}'
                )

            item_subtotal = product.price * requested_qty
            calculated_total += item_subtotal

            order_items.append(OrderItem(
                order=None,
                product_id=product.id,
                name=product.name,
                price=product.price,
                quantity=requested_qty,
            ))

            products_to_update.append({
                "productId": product.id,
                "quantityToDeduct": requested_qty,
            })

        if len(order_items) == 0:
            raise Exception("No se encontraron productos válidos para procesar la orden")

        new_order = Order(
            user_id=user_id,
            totalAmount=calculated_total,
            status="PAID",
            paymentMethod=payment_method or "MOCK_CARD",
            transactionId=f"TX-{int(time.time() * 1000)}-{random.randint(1000, 9999)}",
            createdAt=datetime.now(timezone.utc),
            updatedAt=datetime.now(timezone.utc),
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        for order_item in order_items:
            order_item.order = new_order
            db.add(order_item)
        db.commit()

        shipping = ShippingAddress(
            order=new_order,
            address=shipping_address.get("address", "").strip(),
            city=shipping_address.get("city", "").strip(),
            phone=shipping_address.get("phone", "").strip(),
            notes=shipping_address.get("notes", "") or "",
        )
        db.add(shipping)
        db.commit()

        # Descontar stock
        for prod in products_to_update:
            product = db.query(Product).filter(Product.id == prod["productId"]).first()
            if product:
                product.stock = max(0, product.stock - prod["quantityToDeduct"])
                db.add(product)

        # Vaciar carrito
        cart = db.query(Cart).filter(Cart.user_id == int(user_id)).first()
        if cart:
            cart.items = []
            db.add(cart)

        db.commit()
        db.refresh(new_order)
        return new_order
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def db_get_orders_by_user_id(user_id):
    """Obtiene el historial de ordenes de un usuario."""
    db = SessionLocal()
    try:
        return list(db.query(Order).filter(Order.user_id == int(user_id)).order_by(Order.createdAt.desc()).all())
    finally:
        db.close()


def db_get_order_by_id(order_id, user_id):
    """Obtiene el detalle de una orden por su ID."""
    db = SessionLocal()
    try:
        return db.query(Order).filter(Order.id == int(order_id), Order.user_id == int(user_id)).first()
    except Exception:
        return None
    finally:
        db.close()

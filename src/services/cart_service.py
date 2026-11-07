# src/services/cart_service.py
"""Servicio de Carrito de Compras (equivalente a services/cart.service.js)."""

from src.db.database import SessionLocal
from src.models.cart_model import Cart, CartItem
from src.models.product_model import Product
from src.services.product_service import db_get_product_by_id


def db_get_cart_by_user_id(user_id):
    """Obtiene el carrito de un usuario; si no existe, crea uno vacio."""
    db = SessionLocal()
    try:
        cart = db.query(Cart).filter(Cart.user_id == int(user_id)).first()
        if not cart:
            cart = Cart(user_id=user_id, items=[])
            db.add(cart)
            db.commit()
            db.refresh(cart)
        return cart
    except Exception:
        return None
    finally:
        db.close()


def db_update_cart(user_id, items=None):
    """Actualiza los elementos del carrito validando stock y estado."""
    if items is None:
        items = []

    raw_items = [item for item in items if _to_number(item.get("quantity")) > 0]
    valid_items = []

    db = SessionLocal()
    try:
        cart = db.query(Cart).filter(Cart.user_id == int(user_id)).first()
        if not cart:
            cart = Cart(user_id=user_id, items=[])
            db.add(cart)
            db.commit()
            db.refresh(cart)

        for item in raw_items:
            product_id = item.get("product")
            product = db_get_product_by_id(product_id)
            if not product or not product.status or (product.stock or 0) <= 0:
                continue
            allowed_quantity = min(_to_number(item.get("quantity")), product.stock)
            if allowed_quantity > 0:
                valid_items.append(CartItem(product_id=product.id, quantity=allowed_quantity, cart=cart))

        cart.items = valid_items
        db.commit()
        return cart
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()


def db_sync_cart(user_id, guest_items=None):
    """Fusiona el carrito anonimo con el del usuario autenticado."""
    if guest_items is None:
        guest_items = []

    db = SessionLocal()
    try:
        cart = db.query(Cart).filter(Cart.user_id == int(user_id)).first()
        if not cart:
            cart = Cart(user_id=user_id, items=[])
            db.add(cart)
            db.commit()
            db.refresh(cart)

        for guest_item in guest_items:
            if not guest_item.get("product") or not guest_item.get("quantity"):
                continue
            product = db_get_product_by_id(guest_item.get("product"))
            if not product or not product.status or (product.stock or 0) <= 0:
                continue

            product_id_str = str(product.id)
            existing_index = None
            for idx, item in enumerate(cart.items):
                if str(getattr(item, "product_id", None)) == product_id_str or str(item.product_id) == product_id_str:
                    existing_index = idx
                    break

            if existing_index is not None:
                new_quantity = cart.items[existing_index].quantity + _to_number(guest_item.get("quantity"))
                cart.items[existing_index].quantity = min(new_quantity, product.stock)
            else:
                initial_quantity = min(_to_number(guest_item.get("quantity")), product.stock)
                if initial_quantity > 0:
                    cart.items.append(CartItem(product_id=product.id, quantity=initial_quantity, cart=cart))

        db.commit()
        return cart
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()


def db_remove_item_from_cart(user_id, product_id):
    """Elimina un producto del carrito del usuario."""
    db = SessionLocal()
    try:
        cart = db.query(Cart).filter(Cart.user_id == int(user_id)).first()
        if not cart:
            return None
        cart.items = [item for item in cart.items if item.product_id != int(product_id)]
        db.commit()
        return cart
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()


def db_clear_cart(user_id):
    """Vacia el carrito del usuario."""
    db = SessionLocal()
    try:
        cart = db.query(Cart).filter(Cart.user_id == int(user_id)).first()
        if not cart:
            cart = Cart(user_id=user_id, items=[])
            db.add(cart)
            db.commit()
            db.refresh(cart)
        cart.items = []
        db.commit()
        return cart
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()


def _to_number(value):
    try:
        return int(value) if isinstance(value, (int, float, str)) and str(value).replace(".", "", 1).isdigit() else 0
    except (ValueError, TypeError):
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0

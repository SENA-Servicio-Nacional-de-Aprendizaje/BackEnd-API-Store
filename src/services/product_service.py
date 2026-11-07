# src/services/product_service.py
"""Servicio de Producto (equivalente a services/product.service.js)."""

from src.db.database import SessionLocal
from src.models.product_model import Product, ProductImage


def db_create_product(new_product):
    """Crea un producto y puebla la categoria."""
    if new_product and "categoryId" in new_product and "category_id" not in new_product:
        new_product["category_id"] = new_product.pop("categoryId")

    images = new_product.pop("images", None) or []
    if new_product.get("price") is not None:
        new_product["price"] = float(new_product["price"])
    if new_product.get("stock") is not None:
        new_product["stock"] = int(new_product["stock"])
    if new_product.get("status") is not None:
        new_product["status"] = str(new_product["status"]).lower() in ("true", "1", "t", "yes")

    db = SessionLocal()
    try:
        product = Product(**new_product)
        for img in images:
            product.images.append(ProductImage(url=img.get("url"), isMain=img.get("isMain", False)))
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except Exception:
        db.rollback()
        raise


def db_get_products():
    """Obtiene todos los productos con su categoria."""
    db = SessionLocal()
    try:
        return list(db.query(Product).all())
    finally:
        db.close()


def db_get_product_by_id(id):
    """Obtiene un producto por su ID con su categoria."""
    try:
        db = SessionLocal()
        return db.query(Product).filter(Product.id == int(id)).first()
    except Exception:
        return None


def db_delete_product(id):
    """Elimina un producto por su ID y retorna el documento eliminado."""
    try:
        db = SessionLocal()
        product = db.query(Product).filter(Product.id == int(id)).first()
        if not product:
            return None
        db.delete(product)
        db.commit()
        return product
    except Exception:
        return None


def db_update_product(id, input_data):
    """Actualiza un producto por su ID."""
    if input_data and "categoryId" in input_data and "category_id" not in input_data:
        input_data["category_id"] = input_data.pop("categoryId")

    images = (input_data or {}).pop("images", None) or []
    if (input_data or {}).get("price") is not None:
        input_data["price"] = float(input_data["price"])
    if (input_data or {}).get("stock") is not None:
        input_data["stock"] = int(input_data["stock"])
    if (input_data or {}).get("status") is not None:
        input_data["status"] = str(input_data["status"]).lower() in ("true", "1", "t", "yes")

    try:
        db = SessionLocal()
        product = db.query(Product).filter(Product.id == int(id)).first()
        if not product:
            return None

        for key, value in (input_data or {}).items():
            if hasattr(product, key):
                setattr(product, key, value)

        if images:
            product.images = [ProductImage(url=img.get("url"), isMain=img.get("isMain", False)) for img in images]

        db.commit()
        return product
    except Exception:
        return None

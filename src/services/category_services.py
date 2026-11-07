# src/services/category_services.py
"""Servicio de Categoria (equivalente a services/category.services.js)."""

from datetime import datetime, timezone

from src.db.database import SessionLocal
from src.models.category_model import Category


def insert_category(new_category):
    """Inserta una nueva categoria."""
    db = SessionLocal()
    try:
        category = Category(**new_category)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def db_get_categories():
    """Obtiene todas las categorias."""
    db = SessionLocal()
    try:
        return list(db.query(Category).all())
    finally:
        db.close()


def db_get_category_by_id(id):
    """Obtiene una categoria por su ID."""
    try:
        db = SessionLocal()
        return db.query(Category).filter(Category.id == int(id)).first()
    except Exception:
        return None


def db_update_category(id, input_data):
    """Actualiza una categoria por su ID."""
    try:
        db = SessionLocal()
        category = db.query(Category).filter(Category.id == int(id)).first()
        if not category:
            return None

        for key, value in (input_data or {}).items():
            if hasattr(category, key):
                setattr(category, key, value)

        db.commit()
        return category
    except Exception:
        return None


def db_delete_category(id):
    """Elimina una categoria por su ID."""
    try:
        db = SessionLocal()
        category = db.query(Category).filter(Category.id == int(id)).first()
        if not category:
            return None
        db.delete(category)
        db.commit()
        return category
    except Exception:
        return None


def db_get_default_category():
    """Obtiene o crea la categoria por defecto 'Sin Categoría'."""
    try:
        db = SessionLocal()
        category = (
            db.query(Category).filter(Category.slug == "sin-categoria").first()
            or db.query(Category).filter(Category.name == "Sin Categoría").first()
        )

        if not category:
            category = Category(
                name="Sin Categoría",
                slug="sin-categoria",
                description="Categoría asignada automáticamente a productos no categorizados",
                status=True,
                createdAt=datetime.now(timezone.utc),
                updatedAt=datetime.now(timezone.utc),
            )
            db.add(category)
            db.commit()
            db.refresh(category)
            print('Categoría por defecto "Sin Categoría" (slug: sin-categoria) creada automáticamente')

        return category
    except Exception as error:
        print("Error al obtener/crear la categoría por defecto:", error)
        return None

# src/helpers/serializer.py
"""Utilidad para convertir entidades (SQLAlchemy/MongoEngine) a diccionarios JSON serializables."""

from datetime import datetime

from src.db.database import Base


def to_serializable(value):
    """Convierte de forma recursiva un valor a tipos JSON serializables."""
    if value is None:
        return None

    if isinstance(value, Base):
        data = {}
        for column in value.__table__.columns:
            key = "_id" if column.key == "id" else column.key
            data[key] = to_serializable(getattr(value, column.key, None))
        return data

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [to_serializable(item) for item in value]

    if isinstance(value, tuple):
        return [to_serializable(item) for item in value]

    if isinstance(value, dict):
        return {key: to_serializable(val) for key, val in value.items()}

    return value

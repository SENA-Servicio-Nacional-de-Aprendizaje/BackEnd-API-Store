# src/models/category_model.py
"""Modelo de Categoria (equivalente a models/category.model.js)."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.database import Base


class Category(Base):
    """Categoria de productos (tabla relacional 'category')."""

    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(120), nullable=False, unique=True)
    description = Column(String(255), nullable=False, default="")
    urlImage = Column(String(255), nullable=False, default="/uploads/categories/default-category.png")
    status = Column(Boolean, nullable=False, default=True)
    createdBy = Column(Integer, ForeignKey("user.id"), nullable=True)
    createdAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updatedAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    created_by_user = relationship(
        "User",
        back_populates="created_categories",
    )
    products = relationship("Product", back_populates="category")

# src/models/product_model.py
"""Modelo de Producto (equivalente a models/product.model.js)."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.database import Base


class ProductImage(Base):
    """Imagen asociada a un producto (url + isMain)."""

    __tablename__ = "product_image"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), nullable=False)
    isMain = Column(Boolean, nullable=False, default=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)

    product = relationship("Product", back_populates="images")


class Product(Base):
    """Producto del ecommerce (tabla relacional 'product')."""

    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    referenceCode = Column(String(100), nullable=False, unique=True)
    name = Column(String(150), nullable=False, unique=True)
    description = Column(String(500))
    price = Column(Float, nullable=False, default=0.0)
    stock = Column(Integer, nullable=False, default=1)
    status = Column(Boolean, nullable=False, default=True)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)

    createdAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updatedAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="product")
    ordered_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product")

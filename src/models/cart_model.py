# src/models/cart_model.py
"""Modelos de Carrito de Compras (equivalente a models/cart/*.js)."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.db.database import Base
from src.models.product_model import Product
from src.models.user_model import User


class CartItem(Base):
    """Item del carrito (producto + cantidad)."""

    __tablename__ = "cart_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    cart_id = Column(Integer, ForeignKey("cart.id"), nullable=False)

    product = relationship("Product", back_populates="cart_items")
    cart = relationship("Cart", back_populates="items")


class Cart(Base):
    """Carrito de Compras (tabla relacional 'cart')."""

    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, unique=True)

    createdAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updatedAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

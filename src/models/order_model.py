# src/models/order_model.py
"""Modelos de Orden de Compra (equivalente a models/order/*.js)."""

import random
import time
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.database import Base
from src.models.product_model import Product
from src.models.user_model import User


class OrderItem(Base):
    """Item de orden (producto + metadatos snapshot)."""

    __tablename__ = "order_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    name = Column(String(150), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="ordered_items")


class ShippingAddress(Base):
    """Direccion de envio asociada a una orden."""

    __tablename__ = "order_shipping_address"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    phone = Column(String(30), nullable=False)
    notes = Column(String(255))

    order = relationship("Order", back_populates="shipping_address")


class Order(Base):
    """Orden de Compra (tabla relacional 'order')."""

    __tablename__ = "order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    shipping_address = relationship("ShippingAddress", back_populates="order")

    totalAmount = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="PAID")
    paymentMethod = Column(String(30), nullable=False, default="MOCK_CARD")
    transactionId = Column(String(100), default=lambda: f"TX-{int(time.time() * 1000)}-{random.randint(1000, 9999)}")

    createdAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updatedAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="orders")
    shipping_address = relationship("ShippingAddress", back_populates="order")
# src/models/user_model.py
"""Modelo de Usuario (equivalente a models/user.model.js)."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from src.config.global_config import ALLOWED_ROLES, ROLES
from src.db.database import Base


class User(Base):
    """Usuario del ecommerce (tabla relacional 'user')."""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    nickname = Column(String(20), nullable=False, unique=True)
    email = Column(String(120), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default=ROLES["SUBSCRIBER"])
    status = Column(Boolean, nullable=False, default=True)
    avatarUrl = Column(String(255), nullable=False, default="uploads/avatars/default-avatar.png")

    createdAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updatedAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    created_categories = relationship(
        "Category",
        back_populates="created_by_user",
        cascade="all, delete-orphan",
    )
    carts = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="owner_user")
    contacts = relationship("Contact", back_populates="user")

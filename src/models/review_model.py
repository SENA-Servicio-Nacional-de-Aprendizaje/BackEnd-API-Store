# src/models/review_model.py
"""Modelo de Resena (equivalente a models/review.model.js)."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.database import Base


class Review(Base):
    """Resena de un usuario sobre un producto (tabla relacional 'review')."""

    __tablename__ = "review"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String(1000), nullable=False)

    createdAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updatedAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    owner_user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

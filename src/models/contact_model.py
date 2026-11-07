# src/models/contact_model.py
"""Modelo de Contacto (equivalente a models/contact.model.js)."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.database import Base
from src.models.user_model import User


class Contact(Base):
    """Contacto / suscripcion de un usuario (tabla relacional 'contact')."""

    __tablename__ = "contact"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    label = Column(String(30), nullable=False)
    receiverName = Column(String(50), nullable=False)
    address = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=False)
    isDefault = Column(Boolean, nullable=False, default=False)

    createdAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updatedAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="contacts")

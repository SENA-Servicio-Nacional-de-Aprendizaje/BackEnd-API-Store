# src/db/database.py
"""Configuracion de conexión a base de datos relacional (MySQL + SQLAlchemy)."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/db-store")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Base declarativa de SQLAlchemy para los modelos del proyecto."""


def get_db():
    """Provee una sesion de base de datos (disponible para uso en controladores)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

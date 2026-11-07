# src/config/sql_config.py
"""Configuracion de conexion a base de datos relacional (MySQL + SQLAlchemy)."""

from src.db.database import Base, engine
from src.services.category_services import db_get_default_category


def db_connection():
    """Crea las tablas en la base de datos relacional e inicializa la categoria por defecto."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Connected to MySQL")
        # Inicializar la categoria por defecto si no existe en la base de datos
        db_get_default_category()
    except Exception as error:
        print(error)
        print("Connect Failed! :'(")

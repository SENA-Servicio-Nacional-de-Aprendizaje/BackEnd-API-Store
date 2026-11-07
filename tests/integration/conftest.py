import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import Base
from src.models.cart_model import Cart, CartItem
from src.models.category_model import Category
from src.models.contact_model import Contact
from src.models.order_model import Order, OrderItem, ShippingAddress
from src.models.product_model import Product, ProductImage
from src.models.review_model import Review
from src.models.user_model import User
from src.routes.cart_routes import cart_bp
from src.routes.category_routes import category_bp
from src.routes.order_routes import order_bp
from src.routes.product_routes import product_bp
from src.helpers.jwt_helper import generate_token
from src.services import category_services, order_service, product_service, user_services
from src.middlewares import authentication


API_CATEGORIES_URL = "/api/categories"

engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

category_services.SessionLocal = TestingSessionLocal
order_service.SessionLocal = TestingSessionLocal
product_service.SessionLocal = TestingSessionLocal
user_services.SessionLocal = TestingSessionLocal

Base.metadata.create_all(bind=engine)


@pytest.fixture
def app():
    """App Flask con el blueprint de categorias para pruebas de integracion."""
    application = Flask(__name__)
    application.config["TESTING"] = True
    application.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
    application.register_blueprint(category_bp, url_prefix=API_CATEGORIES_URL)
    application.register_blueprint(product_bp, url_prefix="/api/products")
    application.register_blueprint(cart_bp, url_prefix="/api/cart")
    application.register_blueprint(order_bp, url_prefix="/api/orders")
    return application


@pytest.fixture
def clean_database():
    """Limpia las tablas de categorias y usuarios entre pruebas."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def client(app, clean_database):
    """Cliente de pruebas de Flask (test client) para simular peticiones HTTP."""
    return app.test_client()


@pytest.fixture
def auth_override(monkeypatch):
    """Sobrescribe el servicio de usuarios usado por el middleware de autenticacion."""

    def _get_user_by_email(email):
        db = TestingSessionLocal()
        user = db.query(User).filter(User.email == str(email).lower(), User.status == True).first()
        db.close()
        return user

    monkeypatch.setattr(authentication, "db_get_user_by_email", _get_user_by_email)
    return _get_user_by_email


@pytest.fixture
def admin_token(clean_database, auth_override):
    """Token JWT valido para un usuario con rol de administrador."""
    db = TestingSessionLocal()
    user = User(
        name="Admin Integration",
        nickname="adminint",
        email="admin.integration@store.com",
        password="Secret123",
        role="administrator",
        status=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = generate_token({
        "_id": str(user.id),
        "name": user.name,
        "nickname": user.nickname,
        "email": user.email,
        "role": user.role,
        "avatar": user.avatarUrl,
        "status": user.status,
    })
    db.close()

    return token


@pytest.fixture
def subscriber_token(clean_database, auth_override):
    """Token JWT valido para un usuario con rol de subscriptor."""
    db = TestingSessionLocal()
    user = User(
        name="Subscriber Integration",
        nickname="subint",
        email="subscriber.integration@store.com",
        password="Secret123",
        role="subscriber",
        status=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = generate_token({
        "_id": str(user.id),
        "name": user.name,
        "nickname": user.nickname,
        "email": user.email,
        "role": user.role,
        "avatar": user.avatarUrl,
        "status": user.status,
    })
    db.close()

    return token

"""Pruebas de integracion del controlador de carrito de compras."""

from src.services.category_services import db_get_default_category
from src.services.product_service import db_create_product, db_get_product_by_id

API_CART_URL = "/api/cart"


class TestCartIntegration:
    """Pruebas de integracion para el CRUD del carrito de compras."""

    def test_get_cart_returns_200(self, client, admin_token):
        # Arrange (endpoint protegido por autenticacion)
        # Act
        response = client.get(API_CART_URL + "/", headers={"X-Token": admin_token})

        # Assert
        assert response.status_code == 200
        assert "data" in response.get_json()

    def test_clear_cart_returns_200(self, client, admin_token):
        # Arrange (endpoint protegido por autenticacion)
        # Act
        response = client.delete(API_CART_URL + "/", headers={"X-Token": admin_token})

        # Assert
        assert response.status_code == 200
        assert "data" in response.get_json()

    def test_update_cart_returns_200(self, client, admin_token):
        # Arrange: crear un producto con stock disponible para el carrito
        default_category = db_get_default_category()
        category_id = str(default_category.id) if default_category else None
        assert category_id is not None

        from src.services.product_service import db_create_product as create_product_service

        product = create_product_service({
            "name": "Producto Carrito",
            "referenceCode": "REF-CART-001",
            "category_id": int(category_id),
            "description": "Producto para pruebas de carrito",
            "price": 5.0,
            "stock": 5,
            "status": True,
            "images": [{"url": "/uploads/products/cart-product.png", "isMain": True}],
        })

        # Act
        response = client.put(
            API_CART_URL + "/",
            headers={"X-Token": admin_token},
            json={"items": [{"product": product.id, "quantity": 2}]},
        )

        # Assert
        assert response.status_code == 200
        assert "data" in response.get_json()

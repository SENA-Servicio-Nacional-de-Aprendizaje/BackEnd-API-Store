"""Pruebas de integracion del controlador de ordenes."""

from src.services.category_services import db_get_default_category
from src.services.product_service import db_create_product

API_ORDERS_URL = "/api/orders"


class TestOrdersIntegration:
    """Pruebas de integracion para el CRUD de ordenes."""

    def test_create_order_returns_201(self, client, admin_token):
        # Arrange: crear un producto con stock disponible
        default_category = db_get_default_category()
        category_id = str(default_category.id) if default_category else None
        assert category_id is not None

        product = db_create_product({
            "name": "Producto Orden",
            "referenceCode": "REF-ORDER-001",
            "category_id": int(category_id),
            "description": "Producto para pruebas de ordenes",
            "price": 7.5,
            "stock": 5,
            "status": True,
            "images": [{"url": "/uploads/products/order-product.png", "isMain": True}],
        })

        # Act
        response = client.post(
            API_ORDERS_URL + "/",
            headers={"X-Token": admin_token},
            json={
                "shippingAddress": {
                    "address": "Calle 123 # 45-67",
                    "city": "Medellin",
                    "phone": "3001234567",
                    "notes": "N/A",
                },
                "items": [{"product": product.id, "quantity": 1}],
            },
        )

        # Assert
        assert response.status_code == 201
        assert response.get_json()["msg"] == "Orden de compra creada exitosamente"
        order_id = response.get_json()["data"]["_id"]

        get_response = client.get(f"{API_ORDERS_URL}/{order_id}", headers={"X-Token": admin_token})

        assert get_response.status_code == 200
        assert get_response.get_json()["data"]["_id"] == order_id

    def test_get_order_by_id_with_nonexistent_id_returns_404(self, client, admin_token):
        # Act
        response = client.get(f"{API_ORDERS_URL}/999", headers={"X-Token": admin_token})

        # Assert
        assert response.status_code == 404

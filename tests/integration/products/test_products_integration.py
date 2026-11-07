"""Pruebas de integracion del controlador de productos."""

import io

import pytest

from src.services.category_services import db_get_default_category

API_PRODUCTS_URL = "/api/products"


class TestProductsIntegration:
    """Pruebas de integracion para el CRUD de productos."""

    def test_get_products_returns_200_with_empty_list(self, client):
        # Arrange (endpoint publico: no requiere token)
        # Act
        response = client.get(API_PRODUCTS_URL + "/")

        # Assert
        assert response.status_code == 200
        assert response.get_json()["data"] == []

    def test_get_product_by_id_with_nonexistent_id_returns_404(self, client):
        # Act
        response = client.get(f"{API_PRODUCTS_URL}/999")

        # Assert
        assert response.status_code == 404

    def test_create_product_with_admin_token_returns_201(self, client, admin_token):
        # Arrange
        default_category = db_get_default_category()
        category_id = str(default_category.id) if default_category else None
        assert category_id is not None

        # Act
        response = client.post(
            API_PRODUCTS_URL + "/",
            headers={"X-Token": admin_token},
            data={
                "images": (io.BytesIO(b"contenido-de-imagen-fake"), "product-test.png"),
                "name": "Producto Test",
                "referenceCode": "REF-TEST-001",
                "categoryId": category_id,
                "description": "Producto de prueba para la migracion",
                "price": 10.5,
                "stock": 5,
                "status": True,
            },
        )

        # Assert
        assert response.status_code == 201
        assert response.get_json()["msg"] == "Crea un nuevo producto"
        product_id = response.get_json()["data"]["_id"]

        get_response = client.get(f"{API_PRODUCTS_URL}/{product_id}")

        assert get_response.status_code == 200
        assert get_response.get_json()["data"]["name"] == "Producto Test"

"""Pruebas de integracion del controlador de categorias.

Aqui se valida el flujo completo: router (Blueprint) -> middlewares
(autenticacion/autorizacion) -> controlador -> servicio -> base de datos
(SQLAlchemy con SQLite en memoria), usando el test client de Flask.
"""

import pytest

from src.models.category_model import Category

API_CATEGORIES_URL = "/api/categories"
VALID_ID = "1"
INVALID_ID = "invalido-para-pruebas"


class TestCategoriesIntegration:
    """Pruebas de integracion para el CRUD de categorias."""

    def test_get_categories_public_returns_200_with_empty_list(self, client):
        # Arrange (endpoint publico: no requiere token)
        # Act
        response = client.get(API_CATEGORIES_URL + "/")

        # Assert
        assert response.status_code == 200
        assert response.get_json()["data"] == []

    def test_create_category_with_admin_token_returns_201(self, client, admin_token):
        # Arrange
        payload = {"name": "Audios", "slug": "audios", "description": "Disco de musica", "status": True}

        # Act
        response = client.post(API_CATEGORIES_URL + "/", headers={"X-Token": admin_token}, json=payload)

        # Assert
        assert response.status_code == 201
        assert response.get_json()["msg"] == "Categoría creada exitosamente"
        assert response.get_json()["data"]["name"] == "Audios"

    def test_full_crud_flow_for_category(self, client, admin_token):
        # Arrange: crear una categoria para el flujo completo
        create_response = client.post(
            API_CATEGORIES_URL + "/",
            headers={"X-Token": admin_token},
            json={"name": "Audios", "slug": "audios", "description": "Disco de musica", "status": True},
        )
        assert create_response.status_code == 201
        category_id = create_response.get_json()["data"]["_id"]

        # Act + Assert: obtener la categoria creada
        get_response = client.get(f"{API_CATEGORIES_URL}/{category_id}")

        # Assert
        assert get_response.status_code == 200
        assert get_response.get_json()["data"]["name"] == "Audios"

        # Act + Assert: actualizar la categoria
        update_response = client.patch(
            f"{API_CATEGORIES_URL}/{category_id}",
            headers={"X-Token": admin_token},
            json={"name": "Audios Pro", "description": "Disco de musica actualizado", "status": True},
        )

        # Assert
        assert update_response.status_code == 200
        assert update_response.get_json()["data"]["name"] == "Audios Pro"

        # Act + Assert: eliminar la categoria
        delete_response = client.delete(f"{API_CATEGORIES_URL}/{category_id}", headers={"X-Token": admin_token})

        # Assert
        assert delete_response.status_code == 200

    def test_create_category_without_token_returns_401(self, client):
        # Arrange
        payload = {"name": "Audios", "slug": "audios"}

        # Act
        response = client.post(API_CATEGORIES_URL + "/", json=payload)

        # Assert
        assert response.status_code == 401

    def test_create_category_with_subscriber_token_returns_403(self, client, subscriber_token):
        # Arrange
        payload = {"name": "Audios", "slug": "audios"}

        # Act
        response = client.post(API_CATEGORIES_URL + "/", headers={"X-Token": subscriber_token}, json=payload)

        # Assert
        assert response.status_code == 403

    def test_create_category_with_invalid_token_returns_400(self, client):
        # Arrange
        payload = {"name": "Audios", "slug": "audios"}

        # Act
        response = client.post(API_CATEGORIES_URL + "/", headers={"X-Token": "invalid.token.value"}, json=payload)

        # Assert
        assert response.status_code == 400

    def test_get_category_by_id_with_valid_id_returns_200(self, client, admin_token):
        # Arrange
        create_response = client.post(
            API_CATEGORIES_URL + "/",
            headers={"X-Token": admin_token},
            json={"name": "Audios", "slug": "audios"},
        )
        category_id = create_response.get_json()["data"]["_id"]

        # Act
        response = client.get(f"{API_CATEGORIES_URL}/{category_id}")

        # Assert
        assert response.status_code == 200

    def test_get_category_by_invalid_id_returns_400(self, client):
        # Act
        response = client.get(f"{API_CATEGORIES_URL}/{INVALID_ID}")

        # Assert
        assert response.status_code == 400

    def test_get_category_by_nonexistent_id_returns_404(self, client):
        # Act
        response = client.get(f"{API_CATEGORIES_URL}/{VALID_ID}")

        # Assert
        assert response.status_code == 404

    def test_update_category_with_invalid_id_returns_400(self, client, admin_token):
        # Act
        response = client.patch(
            f"{API_CATEGORIES_URL}/{INVALID_ID}",
            headers={"X-Token": admin_token},
            json={"name": "Audios Pro"},
        )

        # Assert
        assert response.status_code == 400

    def test_update_category_with_nonexistent_id_returns_404(self, client, admin_token):
        # Act
        response = client.patch(
            f"{API_CATEGORIES_URL}/{VALID_ID}",
            headers={"X-Token": admin_token},
            json={"name": "Audios Pro"},
        )

        # Assert
        assert response.status_code == 404

    def test_delete_category_with_invalid_id_returns_400(self, client, admin_token):
        # Act
        response = client.delete(f"{API_CATEGORIES_URL}/{INVALID_ID}", headers={"X-Token": admin_token})

        # Assert
        assert response.status_code == 400

    def test_delete_category_with_nonexistent_id_returns_404(self, client, admin_token):
        # Act
        response = client.delete(f"{API_CATEGORIES_URL}/{VALID_ID}", headers={"X-Token": admin_token})

        # Assert
        assert response.status_code == 404

"""Pruebas unitarias del controlador de categorias.

Se testea el controlador de categoria (src/controllers/category_controller.py)
con el capas de servicio y helpers (get_input_data, request, delete_old_image)
simulados mediante monkeypatch, validando el comportamiento HTTP de cada caso.

Cada test sigue el patron AAA (Arrange - Act - Assert) con comentarios explicitos.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

from sqlalchemy.exc import IntegrityError

from src.controllers import category_controller as category_controller_module
from src.controllers.category_controller import (
    create_category,
    delete_category,
    generate_slug,
    get_categories,
    get_category_by_id,
    update_category,
)

VALID_ID = "1"
INVALID_ID = "id-invalido-para-pruebas"


def invoke(handler, *args, **kwargs):
    """Invoca un handler del controlador y normaliza la respuesta a (Response, status_code).

    Algunos controladores retornan solo el Response (status 200 por defecto) y otros
    retornan una tupla (Response, status_code).
    """
    result = handler(*args, **kwargs)
    if isinstance(result, tuple):
        response, status_code = result
    else:
        response, status_code = result, 200
    return response, status_code


def make_category(url_image="/uploads/categories/category-1234567890.png"):
    """Crea una categoria tipica (SimpleNamespace por su acceso por atributos)."""
    return SimpleNamespace(
        _id=VALID_ID,
        name="Audio",
        slug="audio",
        urlImage=url_image,
        status=True,
    )


class TestGetCategories:
    """Pruebas del endpoint publico GET /api/categories."""

    def test_get_categories_success_returns_200_and_data(self, app, monkeypatch):
        # Arrange
        categories = [
            {"_id": "507f1f77bcf86cd799439011", "name": "Audio", "slug": "audio"},
            {"_id": "507f1f77bcf86cd799439012", "name": "Video", "slug": "video"},
        ]
        mock_db_get_categories = MagicMock(return_value=categories)
        monkeypatch.setattr(category_controller_module, "db_get_categories", mock_db_get_categories)

        # Act
        with app.test_request_context():
            response, status_code = invoke(get_categories)

        # Assert
        assert status_code == 200
        body = response.get_json()
        assert body["msg"] == "Listar Categorias"
        assert len(body["data"]) == 2
        mock_db_get_categories.assert_called_once_with()

    def test_get_categories_returns_200_with_empty_data(self, app, monkeypatch):
        # Arrange
        monkeypatch.setattr(category_controller_module, "db_get_categories", MagicMock(return_value=[]))

        # Act
        with app.test_request_context():
            response, status_code = invoke(get_categories)

        # Assert
        # El backend responde 200 con una lista vacia cuando no hay categorias registradas.
        assert status_code == 200
        body = response.get_json()
        assert body["data"] == []

    def test_get_categories_returns_500_on_unexpected_error(self, app, monkeypatch):
        # Arrange
        monkeypatch.setattr(
            category_controller_module,
            "db_get_categories",
            MagicMock(side_effect=RuntimeError("Error de base de datos")),
        )

        # Act
        with app.test_request_context():
            response, status_code = invoke(get_categories)

        # Assert
        assert status_code == 500


class TestGetCategoryById:
    """Pruebas del endpoint publico GET /api/categories/<id>."""

    def test_get_category_by_id_success(self, app, monkeypatch):
        # Arrange
        category = {"_id": VALID_ID, "name": "Audio", "slug": "audio"}
        monkeypatch.setattr(category_controller_module, "db_get_category_by_id", MagicMock(return_value=category))

        # Act
        with app.test_request_context():
            response, status_code = invoke(get_category_by_id, VALID_ID)

        # Assert
        assert status_code == 200
        body = response.get_json()
        assert body["msg"] == "Categoría obtenida por ID"
        assert body["data"]["name"] == "Audio"

    def test_get_category_by_id_returns_400_for_invalid_id(self, app, monkeypatch):
        # Arrange
        monkeypatch.setattr(category_controller_module, "db_get_category_by_id", MagicMock())

        # Act
        with app.app_context():
            response, status_code = get_category_by_id(INVALID_ID)

        # Assert
        assert status_code == 400

    def test_get_category_by_id_returns_404_when_category_not_found(self, app, monkeypatch):
        # Arrange
        monkeypatch.setattr(category_controller_module, "db_get_category_by_id", MagicMock(return_value=None))

        # Act
        with app.test_request_context():
            response, status_code = invoke(get_category_by_id, VALID_ID)

        # Assert
        assert status_code == 404

    def test_get_category_by_id_returns_500_on_unexpected_error(self, app, monkeypatch):
        # Arrange
        monkeypatch.setattr(
            category_controller_module,
            "db_get_category_by_id",
            MagicMock(side_effect=RuntimeError("Error de base de datos")),
        )

        # Act
        with app.test_request_context():
            response, status_code = invoke(get_category_by_id, VALID_ID)

        # Assert
        assert status_code == 500


class TestCreateCategory:
    """Pruebas del endpoint POST /api/categories."""

    def test_create_category_success_with_explicit_slug(self, app, monkeypatch, fake_request):
        # Arrange
        monkeypatch.setattr(category_controller_module, "get_input_data", lambda: {"name": "Audio", "slug": "audio"})
        mock_insert_category = MagicMock(return_value={"_id": VALID_ID, "name": "Audio", "slug": "audio"})
        monkeypatch.setattr(category_controller_module, "insert_category", mock_insert_category)

        # Act
        with app.test_request_context():
            response, status_code = invoke(create_category)

        # Assert
        assert status_code == 201
        body = response.get_json()
        assert body["msg"] == "Categoría creada exitosamente"
        assert body["data"]["slug"] == "audio"
        mock_insert_category.assert_called_once()

    def test_create_category_success_generates_slug_from_name(self, app, monkeypatch, fake_request):
        # Arrange
        monkeypatch.setattr(category_controller_module, "get_input_data", lambda: {"name": "Audio Basico"})
        mock_insert_category = MagicMock(return_value={"_id": VALID_ID, "name": "Audio Basico", "slug": "audio-basico"})
        monkeypatch.setattr(category_controller_module, "insert_category", mock_insert_category)

        # Act
        with app.test_request_context():
            response, status_code = invoke(create_category)

        # Assert
        assert status_code == 201
        assert mock_insert_category.call_args.args[0]["slug"] == "audio-basico"

    def test_create_category_success_uses_uploaded_image(self, app, monkeypatch, uploaded_request):
        # Arrange
        monkeypatch.setattr(category_controller_module, "get_input_data", lambda: {"name": "Audio"})
        mock_insert_category = MagicMock(return_value={"_id": VALID_ID, "name": "Audio"})
        monkeypatch.setattr(category_controller_module, "insert_category", mock_insert_category)
        monkeypatch.setattr(category_controller_module, "request", uploaded_request)

        # Act
        with app.test_request_context():
            response, status_code = invoke(create_category)

        # Assert
        assert status_code == 201
        assert mock_insert_category.call_args.args[0]["urlImage"] == uploaded_request.uploaded_category_image

    def test_create_category_returns_500_on_validation_error(self, app, monkeypatch, fake_request):
        # Arrange
        validation_error = Exception("La categoria no es valida")
        monkeypatch.setattr(
            category_controller_module,
            "insert_category",
            MagicMock(side_effect=validation_error),
        )

        # Act
        with app.test_request_context():
            response, status_code = invoke(create_category)

        # Assert
        # El controlador centraliza el manejo de errores en un unico except Exception,
        # por lo que cualquier error de validacion se responde con 500.
        assert status_code == 500

    def test_create_category_returns_400_on_duplicate_error(self, app, monkeypatch, fake_request):
        # Arrange
        monkeypatch.setattr(
            category_controller_module,
            "insert_category",
            MagicMock(side_effect=IntegrityError("INSERT INTO category (name) VALUES (:name)", {}, Exception("E11000 duplicate key error"))),
        )

        # Act
        with app.test_request_context():
            response, status_code = invoke(create_category)

        # Assert
        assert status_code == 400
        body = response.get_json()
        assert "duplicidad" in body["msg"].lower()

    def test_create_category_returns_500_on_unexpected_error(self, app, monkeypatch, fake_request):
        # Arrange
        monkeypatch.setattr(category_controller_module, "insert_category", MagicMock(side_effect=RuntimeError("boom")))

        # Act
        with app.test_request_context():
            response, status_code = invoke(create_category)

        # Assert
        assert status_code == 500


class TestUpdateCategory:
    """Pruebas del endpoint PATCH /api/categories/<id>."""

    def test_update_category_success(self, app, monkeypatch, fake_category):
        # Arrange
        monkeypatch.setattr(category_controller_module, "get_input_data", lambda: {"name": "Audio Pro", "slug": "audio-pro"})
        monkeypatch.setattr(category_controller_module, "db_get_category_by_id", MagicMock(return_value=fake_category))
        mock_db_update_category = MagicMock(return_value={"_id": VALID_ID, "name": "Audio Pro"})
        monkeypatch.setattr(category_controller_module, "db_update_category", mock_db_update_category)

        # Act
        with app.test_request_context():
            response, status_code = invoke(update_category, VALID_ID)

        # Assert
        assert status_code == 200
        mock_db_update_category.assert_called_once()
        assert mock_db_update_category.call_args.args[0] == VALID_ID
        assert mock_db_update_category.call_args.args[1]["slug"] == "audio-pro"

    def test_update_category_returns_400_for_invalid_id(self, app, monkeypatch, fake_request):
        # Arrange
        monkeypatch.setattr(category_controller_module, "db_get_category_by_id", MagicMock())

        # Act
        with app.test_request_context():
            response, status_code = update_category(INVALID_ID)

        # Assert
        assert status_code == 400

    def test_update_category_returns_404_when_category_not_found(self, app, monkeypatch, fake_request):
        # Arrange
        monkeypatch.setattr(category_controller_module, "db_get_category_by_id", MagicMock(return_value=None))

        # Act
        with app.test_request_context():
            response, status_code = invoke(update_category, VALID_ID)

        # Assert
        assert status_code == 404

    def test_update_category_returns_400_on_duplicate_error(self, app, monkeypatch, fake_category):
        # Arrange
        monkeypatch.setattr(category_controller_module, "get_input_data", lambda: {"name": "Audio"})
        monkeypatch.setattr(category_controller_module, "db_get_category_by_id", MagicMock(return_value=fake_category))
        monkeypatch.setattr(
            category_controller_module,
            "db_update_category",
            MagicMock(side_effect=IntegrityError("INSERT INTO category (name) VALUES (:name)", {}, Exception("E11000 duplicate key error"))),
        )

        # Act
        with app.test_request_context():
            response, status_code = invoke(update_category, VALID_ID)

        # Assert
        assert status_code == 400

    def test_update_category_returns_500_on_unexpected_error(self, app, monkeypatch, fake_category):
        # Arrange
        monkeypatch.setattr(category_controller_module, "get_input_data", lambda: {"name": "Audio"})
        monkeypatch.setattr(category_controller_module, "db_get_category_by_id", MagicMock(return_value=fake_category))
        monkeypatch.setattr(
            category_controller_module,
            "db_update_category",
            MagicMock(side_effect=RuntimeError("Error al actualizar")),
        )

        # Act
        with app.test_request_context():
            response, status_code = invoke(update_category, VALID_ID)

        # Assert
        assert status_code == 500


class TestDeleteCategory:
    """Pruebas del endpoint DELETE /api/categories/<id>."""

    def test_delete_category_success_deletes_file_and_document(self, app, monkeypatch, fake_category):
        # Arrange
        mock_delete_old_image = MagicMock()
        monkeypatch.setattr(category_controller_module, "delete_old_image", mock_delete_old_image)
        monkeypatch.setattr(category_controller_module, "db_get_category_by_id", MagicMock(return_value=fake_category))
        mock_db_delete_category = MagicMock(return_value={"_id": VALID_ID})
        monkeypatch.setattr(category_controller_module, "db_delete_category", mock_db_delete_category)

        # Act
        with app.test_request_context():
            response, status_code = invoke(delete_category, VALID_ID)

        # Assert
        assert status_code == 200
        mock_delete_old_image.assert_called_once_with(fake_category.urlImage)
        mock_db_delete_category.assert_called_once_with(VALID_ID)

    def test_delete_category_keeps_default_image(self, app, monkeypatch):
        # Arrange
        default_category = SimpleNamespace(
            _id=VALID_ID,
            name="Audio",
            slug="audio",
            urlImage="/uploads/categories/default-category.png",
            status=True,
        )
        mock_delete_old_image = MagicMock()
        monkeypatch.setattr(category_controller_module, "delete_old_image", mock_delete_old_image)
        monkeypatch.setattr(category_controller_module, "db_get_category_by_id", MagicMock(return_value=default_category))
        monkeypatch.setattr(category_controller_module, "db_delete_category", MagicMock(return_value={"_id": VALID_ID}))

        # Act
        with app.test_request_context():
            response, status_code = invoke(delete_category, VALID_ID)

        # Assert
        assert status_code == 200
        mock_delete_old_image.assert_not_called()

    def test_delete_category_returns_400_for_invalid_id(self, app, monkeypatch, fake_request):
        # Arrange
        monkeypatch.setattr(category_controller_module, "db_get_category_by_id", MagicMock())

        # Act
        with app.app_context():
            response, status_code = delete_category(INVALID_ID)

        # Assert
        assert status_code == 400

    def test_delete_category_returns_404_when_category_not_found(self, app, monkeypatch, fake_request):
        # Arrange
        monkeypatch.setattr(category_controller_module, "db_get_category_by_id", MagicMock(return_value=None))

        # Act
        with app.test_request_context():
            response, status_code = invoke(delete_category, VALID_ID)

        # Assert
        assert status_code == 404

    def test_delete_category_returns_500_on_unexpected_error(self, app, monkeypatch, fake_category):
        # Arrange
        monkeypatch.setattr(category_controller_module, "db_get_category_by_id", MagicMock(return_value=fake_category))
        monkeypatch.setattr(
            category_controller_module,
            "db_delete_category",
            MagicMock(side_effect=RuntimeError("Error al eliminar")),
        )

        # Act
        with app.test_request_context():
            response, status_code = invoke(delete_category, VALID_ID)

        # Assert
        assert status_code == 500


class TestGenerateSlug:
    """Pruebas unitarias del helper de slug."""

    def test_generate_slug_normalizes_text(self):
        # Arrange + Act
        result = generate_slug("Productos Audiovisuales!!")

        # Assert
        assert result == "productos-audiovisuales"

    def test_generate_slug_returns_empty_string_for_empty_input(self):
        # Arrange + Act
        result = generate_slug("")

        # Assert
        assert result == ""

    def test_generate_slug_returns_empty_string_for_none_input(self):
        # Arrange + Act
        result = generate_slug(None)

        # Assert
        assert result == ""

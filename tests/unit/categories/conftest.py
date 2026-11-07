from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
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
INVALID_ID = "invalido-para-pruebas"

DEFAULT_CATEGORY_IMAGE = "/uploads/categories/default-category.png"


@pytest.fixture
def fake_category():
    """Categoria tipica usada como dato de entrada en las pruebas."""
    return SimpleNamespace(
        _id=VALID_ID,
        name="Audio",
        slug="audio",
        urlImage="/uploads/categories/category-1234567890.png",
        status=True,
    )


@pytest.fixture
def fake_request():
    """Mock del objeto `request` de Flask para simular archivos subidos."""
    request_mock = MagicMock()
    request_mock.uploaded_category_image = None
    return request_mock


@pytest.fixture
def uploaded_request():
    """Mock de request con una imagen de categoria ya subida."""
    request_mock = MagicMock()
    request_mock.uploaded_category_image = "/uploads/categories/category-9876543210.png"
    return request_mock

# src/controllers/category_controller.py
"""Controlador de Categoria (equivalente a controllers/category.controller.js)."""

import re
from unicodedata import normalize

from flask import jsonify, request
from sqlalchemy.exc import IntegrityError

from src.helpers.file_storage import delete_old_image
from src.helpers.request_helper import get_input_data
from src.helpers.serializer import to_serializable
from src.services.category_services import (
    db_delete_category,
    db_get_categories,
    db_get_category_by_id,
    db_update_category,
    insert_category,
)

DEFAULT_CATEGORY_IMAGE = "/uploads/categories/default-category.png"


def generate_slug(text):
    if not text:
        return ""
    text = str(text)
    text = text.lower().strip()
    text = normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^\w\-]+", "", text)
    text = re.sub(r"\-+", "-", text)
    return text.strip("-")


def get_categories():
    try:
        data = db_get_categories()
        return jsonify({"msg": "Listar Categorias", "data": [to_serializable(d) for d in data]})
    except Exception as error:
        print(error)
        return jsonify({"msg": "Error al obtener todas las categorias"}), 500


def get_category_by_id(id):
    try:
        if not _is_valid_id(id):
            return jsonify({"msg": "ID de categoría inválido"}), 400
        data = db_get_category_by_id(id)
        if not data:
            return jsonify({"msg": "Categoría no encontrada"}), 404
        return jsonify({"msg": "Categoría obtenida por ID", "data": to_serializable(data)})
    except Exception as error:
        print(error)
        return jsonify({"msg": "Error al obtener categoría"}), 500


def create_category():
    try:
        input_data = get_input_data()

        if not input_data.get("slug") and input_data.get("name"):
            input_data["slug"] = generate_slug(input_data.get("name"))

        uploaded = getattr(request, "uploaded_category_image", None)
        if uploaded:
            input_data["urlImage"] = uploaded

        data = insert_category(input_data)

        return jsonify({"msg": "Categoría creada exitosamente", "data": to_serializable(data)}), 201
    except IntegrityError:
        return jsonify({"msg": "Error de duplicidad: Ya existe una categoría con ese nombre o slug"}), 400
    except Exception as error:
        print(error)
        uploaded = getattr(request, "uploaded_category_image", None)
        if uploaded:
            delete_old_image(uploaded)

        return jsonify({"msg": "No se pudo registrar la categoria"}), 500


def update_category(id):
    try:
        if not _is_valid_id(id):
            uploaded = getattr(request, "uploaded_category_image", None)
            if uploaded:
                delete_old_image(uploaded)
            return jsonify({"msg": "ID de categoría inválido"}), 400

        existing_category = db_get_category_by_id(id)
        if not existing_category:
            uploaded = getattr(request, "uploaded_category_image", None)
            if uploaded:
                delete_old_image(uploaded)
            return jsonify({"msg": "La categoría a actualizar no existe"}), 404

        input_data = get_input_data()

        if input_data.get("name") and not input_data.get("slug"):
            input_data["slug"] = generate_slug(input_data.get("name"))

        uploaded = getattr(request, "uploaded_category_image", None)
        existing_image = getattr(existing_category, "urlImage", None)

        if uploaded:
            if existing_image and "default-category.png" not in (existing_image or ""):
                delete_old_image(existing_image)
            input_data["urlImage"] = uploaded
        elif input_data.get("urlImage") == "":
            if existing_image and "default-category.png" not in (existing_image or ""):
                delete_old_image(existing_image)
            input_data["urlImage"] = DEFAULT_CATEGORY_IMAGE

        data = db_update_category(id, input_data)

        return jsonify({"msg": "Categoría actualizada exitosamente", "data": to_serializable(data)})
    except IntegrityError:
        return jsonify({"msg": "Error de duplicidad: Ya existe una categoría con ese nombre o slug"}), 400
    except Exception as error:
        print(error)
        uploaded = getattr(request, "uploaded_category_image", None)
        if uploaded:
            delete_old_image(uploaded)

        return jsonify({"msg": "Error al actualizar la categoría"}), 500


def delete_category(id):
    try:
        if not _is_valid_id(id):
            return jsonify({"msg": "ID de categoría inválido"}), 400

        category = db_get_category_by_id(id)
        if not category:
            return jsonify({"msg": "Categoría no encontrada"}), 404

        if category.urlImage and "default-category.png" not in category.urlImage:
            delete_old_image(category.urlImage)

        data = db_delete_category(id)

        return jsonify({"msg": "Categoría eliminada exitosamente", "data": to_serializable(data)})
    except Exception as error:
        print(error)
        return jsonify({"msg": "Error al eliminar la categoría"}), 500


def _is_valid_id(value):
    """Valida que el identificador sea un entero positivo (PK relacional)."""
    try:
        int(str(value))
        return True
    except Exception:
        return False

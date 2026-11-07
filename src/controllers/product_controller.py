# src/controllers/product_controller.py
"""Controlador de Producto (equivalente a controllers/product.controller.js)."""

from flask import jsonify, request
from sqlalchemy.exc import IntegrityError

from src.helpers.file_storage import delete_multiple_images, delete_old_image
from src.helpers.request_helper import get_input_data
from src.helpers.serializer import to_serializable
from src.services.category_services import db_get_default_category
from src.services.product_service import (
    db_create_product,
    db_delete_product,
    db_get_product_by_id,
    db_get_products,
    db_update_product,
)


def create_product():
    try:
        if not request.uploaded_product_images:
            return jsonify({
                "msg": "Error de validación en los datos del producto",
                "errors": {"images": "El producto debe incluir al menos una (1) imagen"}
            }), 400

        image_objects = [
            {"url": url, "isMain": idx == 0} for idx, url in enumerate(request.uploaded_product_images)
        ]

        input_data = get_input_data()
        input_data["images"] = image_objects

        if not input_data.get("categoryId") or input_data.get("categoryId") in ("", "null", "undefined"):
            default_cat = db_get_default_category()
            if default_cat:
                input_data["categoryId"] = str(default_cat.id)

        data = db_create_product(input_data)

        return jsonify({"msg": "Crea un nuevo producto", "data": to_serializable(data)}), 201
    except IntegrityError:
        if request.uploaded_product_images:
            delete_multiple_images(request.uploaded_product_images)
        return jsonify({
            "msg": "Error de validacion por duplicidad en propiedades unicas",
            "errors": {},
        }), 400
    except Exception as error:
        print(error)
        if request.uploaded_product_images:
            delete_multiple_images(request.uploaded_product_images)

        msg = str(error)
        if "duplicate" in msg.lower() or "unique" in msg.lower():
            return jsonify({
                "msg": "Error de validacion por duplicidad en propiedades unicas",
                "errors": {},
            }), 400
        return jsonify({"msg": "Error: No se pudo crear el producto"}), 500


def get_products():
    try:
        data = db_get_products()
        return jsonify({"msg": "Obtener todos los productos", "data": [to_serializable(d) for d in data]})
    except Exception as error:
        print(error)
        return jsonify({"msg": "ERROR: No pudo obtener los productos"}), 500


def get_product_by_id(id):
    try:
        data = db_get_product_by_id(id)
        if not data:
            return jsonify({"msg": "No se puede obtener un producto que no se encuentra registrado"}), 404
        return jsonify({"msg": "Obtiene un producto por ID", "data": to_serializable(data)})
    except Exception as error:
        print(error)
        return jsonify({"msg": "Error: No pudo obtener producto por ID"}), 500


def update_product(id):
    try:
        uploaded_images = request.uploaded_product_images or []

        if not _is_valid_id(id):
            if uploaded_images:
                delete_multiple_images(uploaded_images)
            return jsonify({"msg": "No se pudo actualizar el producto, por que el ID es invalido"}), 400

        current_product = db_get_product_by_id(id)
        if not current_product:
            if uploaded_images:
                delete_multiple_images(uploaded_images)
            return jsonify({"msg": "No se pudo actualizar el producto, por que no se encuentra registrado"}), 404

        current_images = [dict(img) for img in (current_product.images or [])]
        # Normalizar embedded documents to serializable dict
        current_images = [{"url": img.get("url") if hasattr(img, "get") else img.url, "isMain": img.get("isMain", False) if hasattr(img, "get") else img.isMain} for img in current_images]

        input_data = get_input_data()

        # Eliminar imagenes
        if input_data.get("deleteAllImages") in (True, "true"):
            all_urls = [img["url"] for img in current_images]
            delete_multiple_images(all_urls)
            current_images = []
            input_data.pop("deleteAllImages", None)
        elif input_data.get("deleteImageUrl"):
            target_delete_url = str(input_data.get("deleteImageUrl")).strip()
            delete_old_image(target_delete_url)
            current_images = [img for img in current_images if img["url"] != target_delete_url]
            input_data.pop("deleteImageUrl", None)
        elif isinstance(input_data.get("deleteImageUrls"), list):
            delete_multiple_images(input_data["deleteImageUrls"])
            urls_to_delete = set(input_data["deleteImageUrls"])
            current_images = [img for img in current_images if img["url"] not in urls_to_delete]
            input_data.pop("deleteImageUrls", None)

        # Anadir nuevas imagenes
        if uploaded_images:
            if len(current_images) + len(uploaded_images) > 9:
                delete_multiple_images(uploaded_images)
                return jsonify({
                    "msg": "Error de validación en las imágenes",
                    "errors": {"images": "No se pueden asociar más de nueve (9) imágenes a un producto"}
                }), 400

            new_images = [{"url": url, "isMain": False} for url in uploaded_images]
            current_images = current_images + new_images

        # Cambiar imagen principal
        if input_data.get("mainImageUrl"):
            target_main_url = str(input_data.get("mainImageUrl")).strip()
            exists = any(img["url"] == target_main_url for img in current_images)
            if exists:
                for img in current_images:
                    img["isMain"] = img["url"] == target_main_url
            input_data.pop("mainImageUrl", None)

        # Asegurar al menos una imagen principal
        if len(current_images) > 0:
            has_main = any(img.get("isMain") for img in current_images)
            if not has_main:
                current_images[0]["isMain"] = True

        input_data["images"] = current_images

        data = db_update_product(id, input_data)

        return jsonify({"msg": "Actualiza un producto", "data": to_serializable(data)})
    except IntegrityError:
        if request.uploaded_product_images:
            delete_multiple_images(request.uploaded_product_images)

        return jsonify({
            "msg": "Error de validacion por duplicidad en propiedades unicas",
            "errors": {},
        }), 400
    except Exception as error:
        print(error)
        if request.uploaded_product_images:
            delete_multiple_images(request.uploaded_product_images)

        msg = str(error)
        if "duplicate" in msg.lower() or "unique" in msg.lower():
            return jsonify({
                "msg": "Error de validacion por duplicidad en propiedades unicas",
                "errors": {},
            }), 400
        if "ObjectId" in msg or "invalid" in msg.lower():
            return jsonify({"msg": "No se pudo actualizar el producto, por que el ID es invalido"}), 400
        return jsonify({"msg": "Error: No pudo actualizar el producto por su ID"}), 500


def delete_product(id):
    try:
        if not _is_valid_id(id):
            return jsonify({"msg": "No se puede eliminar, por que el ID proporcionado es invalido"}), 400

        data = db_delete_product(id)
        if not data:
            return jsonify({"msg": "No se puede eliminar un producto que no se encuentra registrado"})

        _image_urls = []
        for img in (data.images or []):
            if hasattr(img, "url"):
                _image_urls.append(img.url)
            elif isinstance(img, dict):
                _image_urls.append(img.get("url"))
        delete_multiple_images(_image_urls)

        return jsonify({"msg": "Elimina un producto", "data": to_serializable(data)})
    except Exception as error:
        print(error)
        return jsonify({"msg": "ERROR: No pudo eliminar el producto"}), 500


def _is_valid_id(value):
    try:
        int(str(value))
        return True
    except Exception:
        return False

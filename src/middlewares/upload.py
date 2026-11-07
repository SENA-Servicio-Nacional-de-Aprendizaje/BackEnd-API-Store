# src/middlewares/upload.py
"""Middleware de carga de archivos (equivalente a middlewares/upload*.js y handleUpload*.js)."""

import os
import random
import time
from functools import wraps

from flask import jsonify, request

ALLOWED_MIME_TYPES = {"image/jpg", "image/jpeg", "image/pjpeg", "image/png", "image/webp"}
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def _validate_file(file_storage):
    """Valida formato y tamano (max 2MB) de un archivo. Retorna (ok, error_msg)."""
    ext = os.path.splitext(file_storage.filename)[1].lower()
    mime = (file_storage.mimetype or "").lower()

    if mime not in ALLOWED_MIME_TYPES and ext not in ALLOWED_EXTS:
        return False, "Formato no permitido. Solo se aceptan imágenes (JPG, JPEG, PNG, WEBP)."

    # Verificar tamano
    file_storage.seek(0, 2)
    size = file_storage.tell()
    file_storage.seek(0)
    if size > 2 * 1024 * 1024:
        return False, "LIMIT_FILE_SIZE"

    return True, None


def handle_upload_avatar(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        request.uploaded_avatar = None
        file = request.files.get("avatarUrl")
        if file and file.filename:
            ok, err = _validate_file(file)
            if not ok:
                if err == "LIMIT_FILE_SIZE":
                    return jsonify({
                        "msg": "Error de validación en la imagen",
                        "errors": ["El peso de la imagen no puede superar los 2MB"]
                    }), 400
                return jsonify({
                    "msg": "Error de validación en la imagen",
                    "errors": [err]
                }), 400

            dir_path = os.path.join("public", "uploads", "avatars")
            os.makedirs(dir_path, exist_ok=True)
            ext = os.path.splitext(file.filename)[1].lower()
            unique_suffix = f"{int(time.time() * 1000)}-{random.randint(0, 10 ** 9)}"
            filename = f"avatar-{unique_suffix}{ext}"
            file.save(os.path.join(dir_path, filename))
            request.uploaded_avatar = f"uploads/avatars/{filename}"

        return view_func(*args, **kwargs)

    return wrapper


def handle_upload_category_image(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        request.uploaded_category_image = None
        file = request.files.get("urlImage")
        if file and file.filename:
            ok, err = _validate_file(file)
            if not ok:
                if err == "LIMIT_FILE_SIZE":
                    return jsonify({
                        "msg": "Error de validación en la imagen",
                        "errors": ["El peso de la imagen no puede superar los 2MB"]
                    }), 400
                return jsonify({
                    "msg": "Error de validación en la imagen",
                    "errors": [err]
                }), 400

            dir_path = os.path.join("public", "uploads", "categories")
            os.makedirs(dir_path, exist_ok=True)
            ext = os.path.splitext(file.filename)[1].lower()
            unique_suffix = f"{int(time.time() * 1000)}-{random.randint(0, 10 ** 9)}"
            filename = f"category-{unique_suffix}{ext}"
            file.save(os.path.join(dir_path, filename))
            request.uploaded_category_image = f"/uploads/categories/{filename}"

        return view_func(*args, **kwargs)

    return wrapper


def handle_upload_product_images(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        request.uploaded_product_images = []
        files = request.files.getlist("images")
        if not files or all(not f.filename for f in files):
            # No se envio archivo; dejar lista vacia (el controlador decide si es requerido)
            return view_func(*args, **kwargs)

        files = [f for f in files if f and f.filename]
        if len(files) > 9:
            return jsonify({
                "msg": "Error de validación en las imágenes",
                "errors": ["No se pueden subir más de 9 imágenes por producto"]
            }), 400

        saved_filenames = []
        try:
            for f in files:
                ok, err = _validate_file(f)
                if not ok:
                    # Limpiar ya guardados
                    for name in saved_filenames:
                        try:
                            os.remove(os.path.join("public", name.lstrip("/")))
                        except OSError:
                            pass
                    if err == "LIMIT_FILE_SIZE":
                        return jsonify({
                            "msg": "Error de validación en las imágenes",
                            "errors": ["Ninguna imagen individual puede superar los 2MB"]
                        }), 400
                    return jsonify({
                        "msg": "Error de validación en las imágenes",
                        "errors": [err]
                    }), 400

                dir_path = os.path.join("public", "uploads", "products")
                os.makedirs(dir_path, exist_ok=True)
                ext = os.path.splitext(f.filename)[1].lower()
                unique_suffix = f"{int(time.time() * 1000)}-{random.randint(0, 10 ** 9)}"
                filename = f"product-{unique_suffix}{ext}"
                f.save(os.path.join(dir_path, filename))
                saved_filenames.append(f"/uploads/products/{filename}")

            request.uploaded_product_images = saved_filenames
        except Exception as error:
            for name in saved_filenames:
                try:
                    os.remove(os.path.join("public", name.lstrip("/")))
                except OSError:
                    pass
            return jsonify({
                "msg": "Error de validación en las imágenes",
                "errors": [str(error)]
            }), 400

        return view_func(*args, **kwargs)

    return wrapper

# src/helpers/file_storage.py
"""Utilidades para gestionar la eliminacion segura de archivos locales
(equivalente a helpers/file-storage.js)."""

import os


def delete_old_image(image_path):
    """Elimina un archivo del disco si existe y no es la imagen por defecto."""
    if not image_path or "default-avatar.png" in image_path:
        return

    try:
        full_path = os.path.join(os.getcwd(), "public", image_path.lstrip("/"))
        # Normalizar: original usa public/<imagePath>
        if image_path.startswith("/uploads"):
            full_path = os.path.join(os.getcwd(), "public", image_path.lstrip("/"))
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception as error:
        print("Error al eliminar la imagen previa:", error)


def delete_multiple_images(image_paths=None):
    """Elimina una lista de archivos del disco."""
    if not image_paths:
        return
    for image_path in image_paths:
        delete_old_image(image_path)

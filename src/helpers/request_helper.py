# src/helpers/request_helper.py
"""Ayudante para obtener el body de la peticion (equivalente a req.body)."""

from flask import g, request


def get_input_data():
    """Obtiene los datos de entrada de la peticion, JSON o form-data."""
    content_type = request.content_type or ""
    if "multipart/form-data" in content_type:
        data = request.form.to_dict()
    else:
        data = request.get_json(silent=True)
        if data is None:
            data = {}

    # Si el middleware without-role marco la peticion, eliminar role/status
    if isinstance(data, dict) and getattr(g, "remove_role", False):
        data.pop("role", None)
        data.pop("status", None)

    return data

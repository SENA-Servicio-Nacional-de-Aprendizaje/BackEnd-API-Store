# src/middlewares/without_role.py
"""Middleware que elimina role/status del body (equivalente a without-role.middleware.js)."""

from functools import wraps

from flask import g


def remove_role(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # Marca la peticion para que get_input_data omite role y status
        g.remove_role = True
        return view_func(*args, **kwargs)

    return wrapper

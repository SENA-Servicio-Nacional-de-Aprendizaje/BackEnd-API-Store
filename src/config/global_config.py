# src/config/global_config.py
"""Definicion global de roles de usuario (equivalente a config/global.config.js)."""

# Retorna un objeto con todos los roles permitidos
ROLES = {
    "SUPER_ADMIN": "super administrador",
    "ADMIN": "administrator",
    "EDITOR": "editor",
    "AUTHOR": "author",
    "CONTRIBUTOR": "contributor",
    "SUBSCRIBER": "subscriber",
}

# Listado de los roles permitidos
ALLOWED_ROLES = list(ROLES.values())

ROLE_LABELS = {
    ROLES["SUPER_ADMIN"]: "Super Administrador",
    ROLES["ADMIN"]: "Administrador",
    ROLES["EDITOR"]: "Editor",
    ROLES["AUTHOR"]: "Autor",
    ROLES["CONTRIBUTOR"]: "Contribuidor",
    ROLES["SUBSCRIBER"]: "Subscriptor",
}

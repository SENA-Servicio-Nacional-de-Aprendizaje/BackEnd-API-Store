import pytest
from flask import Flask


@pytest.fixture
def app():
    """Fixture de PyTest que expone una aplicacion Flask lista para ejecutar los controladores.

    Se utiliza en las pruebas unitarias para tener el contexto de aplicacion
    requerido por `flask.jsonify` sin levantar el servidor completo.
    """
    application = Flask(__name__)
    application.config["TESTING"] = True
    return application

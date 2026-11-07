# app.py
"""Punto de entrada de la aplicacion Flask (equivalente a src/index.js)."""

import os

from dotenv import load_dotenv
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

from src.config.sql_config import db_connection
from src.routes.auth_routes import auth_bp
from src.routes.cart_routes import cart_bp
from src.routes.category_routes import category_bp
from src.routes.order_routes import order_bp
from src.routes.product_routes import product_bp
from src.routes.roles_routes import roles_bp
from src.routes.user_routes import user_bp

load_dotenv()

app = Flask(__name__)
PORT = int(os.getenv("PORT") or 3001)

# Conexion a la base de datos
db_connection()

# Middlewares
CORS(app)  # Habilita CORS (equivalente a app.use(cors()))
# Servir archivos estaticos de /uploads (equivalente a express.static)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"msg": "Sitio funcionando! :)"})


@app.route("/uploads/<path:filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(os.path.join("public", "uploads"), filename)


# Endpoints agrupados por entidad
app.register_blueprint(user_bp, url_prefix="/api/users")
app.register_blueprint(product_bp, url_prefix="/api/products")
app.register_blueprint(category_bp, url_prefix="/api/categories")
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(roles_bp, url_prefix="/api/roles")
app.register_blueprint(cart_bp, url_prefix="/api/cart")
app.register_blueprint(order_bp, url_prefix="/api/orders")


if __name__ == "__main__":
    print(f"Server running on http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)

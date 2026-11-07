# Python-API-Store (Flask)

API REST para una tienda (replica del proyecto Node/Express `BackEnd-Store`), implementada con
**Python + Flask + MongoDB (MongoEngine)**.

Cada funcionalidad está comentada para facilitar el aprendizaje.

---

## 1. Inicializar el repositorio

```bash
# Clonar o crear el repositorio
git init
git remote add origin https://github.com/<tu-usuario>/Python-API-Store.git

# Crear la estructura base
mkdir -p src/{config,models,helpers,services,middlewares,controllers,routes}
mkdir -p public/uploads/{avatars,categories,products}
touch src/{config,models,helpers,services,middlewares,controllers,routes}/__init__.py
```

## 2. Crear y activar el entorno virtual

```bash
python3 -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows (PowerShell)
# .\venv\Scripts\Activate.ps1
```

## 3. Instalar dependencias

Todas las dependencias están declaradas en `requirements.txt`.

```bash
pip install -r requirements.txt
```

### Dependencias principales

| Paquete | Propósito |
| --- | --- |
| `Flask` | Framework web |
| `Flask-Cors` | Habilitar CORS |
| `pymongo` | Driver de MongoDB |
| `mongoengine` | ODM (equivalente a Mongoose) |
| `PyJWT` | JSON Web Tokens |
| `bcrypt` | Encriptación de contraseñas |
| `python-dotenv` | Variables de entorno |
| `Werkzeug` | Utilidades (archivos, seguridad) |

## 4. Configurar variables de entorno

Crear el archivo `.env` a partir de `.env.example`:

```bash
cp .env.example .env
```

Contenido de `.env`:

```env
PORT=3001
JWT_SEED=123456789ABCabc
DB_URI=mongodb://localhost:27017/db-store
```

## 5. Instalar y ejecutar MongoDB

* **Local**: instalar MongoDB Community Edition y ejecutar el servicio (`mongod`).
* **Atlas**: usar la URI proporcionada por MongoDB Atlas en `DB_URI`.

La aplicación crea automáticamente la categoría por defecto **"Sin Categoría"** al conectarse.

## 6. Estructura del proyecto

```
Python-API-Store/
├── app.py                      # Punto de entrada (equivalente a src/index.js)
├── requirements.txt
├── .env.example
├── src/
│   ├── config/                 # Configuración (roles y MongoDB)
│   ├── models/                 # Modelos MongoEngine (equivalente a Mongoose)
│   ├── helpers/                # Bcrypt, JWT, archivos, serializador
│   ├── services/               # Lógica de acceso a datos
│   ├── middlewares/            # Auth, autorización, upload, without-role
│   ├── controllers/            # Controladores por entidad
│   └── routes/                 # Blueprints (rutas)
└── public/uploads/             # Archivos estáticos (avatares, categorías, productos)
```

## 7. Ejecutar la aplicación

```bash
python app.py
```

El servidor se levanta en `http://localhost:3001` (o el `PORT` definido).
Endpoint de salud: `GET /health`.

## 8. Funcionalidades replicadas

* Autenticación JWT (login, registro público, renovación de token).
* Usuarios (CRUD) con subida de avatar, roles y permisos.
* Roles (listado).
* Productos (CRUD, hasta 9 imágenes, imagen principal, eliminación en cascada).
* Categorías (CRUD, imagen).
* Carrito de compras (get, update, sync merge, remove item, clear).
* Órdenes de compra (creación mock, descuento de stock, vaciado de carrito, historial).
* Servicio de archivos estáticos `/uploads`.

## 9. Probar la API

Se puede usar Bruno/Postman o cualquier cliente HTTP. Los headers relevantes:

* `X-Token: <jwt>` para las rutas protegidas.
* `Content-Type: application/json` para JSON.
* `multipart/form-data` para subida de archivos.

## 10. Comandos útiles de desarrollo

```bash
# Ejecutar en modo debug
FLASK_DEBUG=1 python app.py

# Verificar sintaxis de todos los módulos
python -m compileall src app.py
```

## 11. Notas

* El proyecto replica la arquitectura MVC del proyecto Node/Express original.
* Los comentarios en el código explican cada funcionalidad.
* Mantener sincronizado `requirements.txt` al añadir nuevas dependencias
  (`pip freeze > requirements.txt`).

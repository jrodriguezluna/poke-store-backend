# PokéStore Backend (FastAPI)

API REST para la plataforma **PokéStore**, desarrollada con **FastAPI**, **SQLAlchemy** y **MySQL**.

---

## 1. Requisitos previos

- **Python 3.10+** (recomendado 3.12)
- **pip**

---

## 2. Instalación y configuración

Clonar el repositorio y ubicarse en la raíz del proyecto:

```bash
git clone <url-del-repositorio>
cd poke-store-backend
```

### Crear y activar el entorno virtual

En **Linux / macOS**:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

En **Windows** (PowerShell / CMD):
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Instalar dependencias

```bash
pip install -r requirements.lock.txt
```

---

## 3. Variables de entorno (`.env`)

Copiar el archivo de plantilla `.env.example` a `.env`:

```bash
cp .env.example .env
```

Completar los valores en `.env` con los datos de conexión a la base de datos MySQL (por ejemplo, una instancia de AWS RDS o MySQL local):

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=pokestore
UPLOAD_DIR=uploads
CORS_ORIGINS=http://localhost:5173
```

> **Nota:** El archivo `.env` contiene credenciales sensibles y está excluido del control de versiones mediante `.gitignore`.

---

## 4. Inicialización de la base de datos

### Base de datos nueva

Para crear las tablas e insertar los datos iniciales en una base de datos vacía:

```bash
python -m app.scripts.init_db
```

> **Advertencia:** `init_db` elimina y recrea todas las tablas. No lo ejecutes sobre una base de datos con información que quieras conservar.

### Base de datos existente

Para agregar columnas que falten sin borrar usuarios, productos ni pedidos:

```bash
python -m app.scripts.migrate_schema
```

Ejecuta esta migración antes de iniciar el backend cuando actualices el código.

> **Importante:** Ejecuta el comando correspondiente desde la **raíz del proyecto** utilizando el parámetro `-m`. Ejecutar un script directamente desde `app/scripts/` puede generar `ModuleNotFoundError: No module named 'app'` y no cargar el archivo `.env`.

### Usuario administrador generado por defecto:
- **Email:** `admin@pokestore.cl`
- **Contraseña:** `admin123`
- **Rol:** `admin`

---

## 5. Ejecutar el servidor

Con el entorno virtual activo, iniciar el servidor de desarrollo:

```bash
uvicorn app.main:app --reload --port 8000
```

Verificar que el servicio y la conexión a la base de datos estén operativos:
```bash
curl http://localhost:8000/api/health
# Respuesta esperada: {"ok": true}
```

---

## 6. Documentación interactiva de la API

FastAPI genera automáticamente documentación interactiva accesible desde el navegador:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs) (permite consultar esquemas y probar peticiones interactivamente).
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 7. Integración con el Frontend (Vite)

Si el cliente frontend utiliza Vite en desarrollo (`http://localhost:5173`), configurar el proxy inverso en `vite.config.js` para redirigir las peticiones del backend y los archivos estáticos subidos:

```javascript
// vite.config.js
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/uploads': 'http://localhost:8000',
    },
  },
});
```

---

## 8. Estructura del proyecto

```text
poke-store-backend/
├── app/
│   ├── config.py           # Configuración y lectura de variables de entorno
│   ├── database.py         # Conexión SQLAlchemy y generador de sesiones
│   ├── main.py             # Aplicación FastAPI, middlewares y rutas
│   ├── models.py           # Modelos de base de datos ORM
│   ├── schemas.py          # Esquemas Pydantic de entrada y salida
│   ├── security.py         # Hashing y verificación de contraseñas con bcrypt
│   ├── routers/            # Endpoints agrupados por recurso
│   │   ├── contacto.py
│   │   ├── pedidos.py
│   │   ├── productos.py
│   │   └── usuarios.py
│   └── scripts/
│       └── init_db.py      # Script de inicialización y seed de datos
├── uploads/                # Directorio local para almacenamiento de imágenes
├── .env.example            # Plantilla de variables de entorno
├── .gitignore              # Reglas de exclusión para Git
├── requirements.txt        # Dependencias principales
├── requirements.lock.txt   # Dependencias con versiones exactas
└── README.md
```


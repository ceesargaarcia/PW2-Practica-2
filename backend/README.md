# 🏜️ Desert Vault – Backend Python (Práctica 2)

Backend reescrito en **Python / FastAPI** que expone exactamente la misma API REST
que el backend Node.js/Express original, permitiendo que el frontend **Svelte 5**
funcione sin ningún cambio.

---

## Arquitectura por capas

```
routers/        ← Controladores HTTP (reciben la petición, delegan al servicio)
services/       ← Lógica de negocio (orquesta repositorios, lanza excepciones de dominio)
repositories/   ← Acceso a datos (única capa que toca SQLAlchemy/DB)
models/         ← Modelos ORM (tablas de la BD)
schemas/        ← Esquemas Pydantic (validación de entrada, serialización de salida)
middleware/     ← Dependencias FastAPI para autenticación JWT
core/           ← Configuración, seguridad (JWT + bcrypt), excepciones de dominio
db/             ← Engine SQLAlchemy y factory de sesiones
```

---

## Requisitos previos

| Herramienta | Versión mínima |
|-------------|----------------|
| Python      | 3.12           |
| pip         | 23+            |

---

## Instalación y ejecución

```bash
cd backend-python
cp .env.example .env          # edita JWT_SECRET si quieres
pip install -r requirements.txt
```

### 1. Crear el primer administrador

La API pública no permite registrarse como admin (medida de seguridad).
El primer admin se crea ejecutando el script incluido en el proyecto:

```bash
python create_admin.py
```

Esto crea automáticamente un usuario administrador con las siguientes credenciales:

| Campo   | Valor            |
|---------|------------------|
| Usuario | `admin`          |
| Email   | `admin@test.com` |
| Password| `Admin123`       |
| Rol     | `admin`          |

Si necesitas credenciales distintas puedes pasarlas como argumentos:

```bash
python create_admin.py --username cesar --email cesar@example.com --password MiPassword123
```

### 2. Arrancar el servidor

```bash
uvicorn main:app --reload --port 3000
```

El servidor arranca en **http://localhost:3000** (mismo puerto que el Node.js original).

### Documentación interactiva

Abre **http://localhost:3000/api/docs** para el Swagger UI generado automáticamente.

---

## Integración con el frontend Svelte 5

El frontend **no necesita ningún cambio**.

```bash
# Terminal 1 – backend Python
uvicorn main:app --reload --port 3000

# Terminal 2 – frontend Svelte
cd frontend
npm install
npm run dev   # http://localhost:5173
```

### Build de producción (frontend integrado en el backend)

```bash
cd frontend && npm run build   # genera backend-python/public/
cd ../backend-python && uvicorn main:app --port 3000
```

---

## Cómo promover un usuario a admin

Una vez que existe al menos un admin, puede promover a otros usuarios desde el
panel de administración del frontend, o directamente via API:

```bash
# 1. Login como admin para obtener token
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"Admin123"}'

# 2. Promover usuario (sustituir TOKEN y USER_ID)
curl -X PUT http://localhost:3000/api/users/USER_ID/role \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"admin"}'
```

---

## Endpoints de la API REST

### Autenticación (`/api/auth`)
| Método | Ruta        | Body requerido            | Acceso  |
|--------|-------------|---------------------------|---------|
| POST   | `/register` | username, email, password | Público |
| POST   | `/login`    | email, password           | Público |
| POST   | `/logout`   | —                         | Público |

> **Nota:** el campo `role` en `/register` es ignorado. Todos los registros son
> siempre `user`. Para crear admins usar `create_admin.py` o el endpoint de rol.

### Productos (`/api/products`)
| Método | Ruta    | Acceso      |
|--------|---------|-------------|
| GET    | `/`     | Autenticado |
| GET    | `/{id}` | Autenticado |
| POST   | `/`     | Admin       |
| PUT    | `/{id}` | Admin       |
| DELETE | `/{id}` | Admin       |

### Usuarios (`/api/users`)
| Método | Ruta         | Acceso      |
|--------|--------------|-------------|
| GET    | `/`          | Admin       |
| GET    | `/me`        | Autenticado |
| PUT    | `/{id}/role` | Admin       |
| DELETE | `/{id}`      | Admin       |

---

## Variables de entorno

| Variable             | Descripción                      | Default                       |
|----------------------|----------------------------------|-------------------------------|
| `DATABASE_URL`       | URL de SQLAlchemy                | `sqlite:///./desert_vault.db` |
| `JWT_SECRET`         | Clave secreta para firmar tokens | `changeme_secret`             |
| `JWT_ALGORITHM`      | Algoritmo JWT                    | `HS256`                       |
| `JWT_EXPIRE_MINUTES` | Expiración del token en minutos  | `1440` (24 h)                 |

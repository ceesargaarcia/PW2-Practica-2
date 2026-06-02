# Memoria de uso de Inteligencia Artificial — Práctica 2

## Índice

1. [Contexto y enfoque de uso](#1-contexto-y-enfoque-de-uso)
2. [Registro de prompts e iteraciones](#2-registro-de-prompts-e-iteraciones)
3. [Análisis crítico: errores de la IA y correcciones manuales](#3-análisis-crítico-errores-de-la-ia-y-correcciones-manuales)
   - [Error 1 — Incompatibilidad de versiones: passlib + bcrypt](#error-1--incompatibilidad-de-versiones-passlib--bcrypt)
   - [Error 2 — Fallo de seguridad: escalada de privilegios en el registro](#error-2--fallo-de-seguridad-escalada-de-privilegios-en-el-registro)
   - [Error 3 — Dos bugs de comportamiento HTTP: redirect que rompe la autenticación y código de estado incorrecto en token expirado](#error-3--dos-bugs-de-comportamiento-http-redirect-que-rompe-la-autenticación-y-código-de-estado-incorrecto-en-token-expirado)

---

## 1. Contexto y enfoque de uso

El objetivo de esta práctica era reemplazar el backend Node.js/Express/MongoDB de la Práctica 1 por uno nuevo escrito en Python con FastAPI, manteniendo el mismo contrato de API para que el frontend Svelte 5 siguiera funcionando sin modificaciones.

Usé Claude AI como asistente de desarrollo durante todo el proceso, pero no de forma ciega: cada fragmento generado fue revisado, ejecutado y, en varios casos, corregido manualmente. El flujo real fue:

1. Describía qué quería construir y por qué.
2. Claude generaba una primera versión.
3. La ejecutaba, veía qué fallaba o qué no encajaba, y reformulaba.
4. En algunos casos la corrección fue manual directamente sobre el fichero.

---

## 2. Registro de prompts e iteraciones

### Prompt 1 — Definir la estructura de carpetas y capas

**Contexto:** Antes de escribir ningún fichero necesitaba decidir cómo organizar el proyecto en capas limpias, que es uno de los requisitos explícitos de la práctica.

**Prompt:**

> Quiero montar un backend FastAPI para reemplazar uno en Node.js/Express. Tiene dos recursos: usuarios y productos, con autenticación JWT. ¿Cómo organizarías las carpetas siguiendo arquitectura limpia con separación de responsabilidades?

**Respuesta de la IA (resumen):**

```
routers/      → reciben HTTP, delegan al servicio
services/     → lógica de negocio
repositories/ → acceso a datos (ORM)
models/       → modelos SQLAlchemy
schemas/      → Pydantic (validación entrada/salida)
core/         → configuración, seguridad, excepciones
db/           → engine y sesión
```

**Por qué fue útil:** La estructura propuesta coincidía con lo que el profesor llama "arquitectura en capas" y con el patrón que ya conocía del TFG. Me sirvió como punto de partida sólido sin necesidad de iterar.

---

### Prompt 2 — Convertir los modelos Mongoose a SQLAlchemy

**Contexto:** Tenía los modelos `User.js` y `Product.js` de la práctica anterior hechos con Mongoose y necesitaba convertirlos a tablas SQLAlchemy manteniendo los mismos campos.

**Prompt:**

> Tengo estos dos modelos Mongoose. Conviértelos a SQLAlchemy usando la sintaxis moderna con mapped_column y Mapped. User tiene: username único, email único, password, role (user/admin) y createdAt. Product tiene: name, description, price, category, stock, active, imageUrl, createdBy como foreign key a User, createdAt y updatedAt. Usa SQLite.

Le pegué directamente el contenido de `User.js` y `Product.js` junto al prompt.

**Problema detectado:** La IA generó los IDs como `Integer` con autoincremento, el tipo estándar de SQLAlchemy. Sin embargo, el backend anterior usaba MongoDB cuyos IDs son strings. El frontend Svelte almacena el `userId` como string en el JWT y lo usa directamente en las peticiones, por lo que habría una incompatibilidad de tipos al comparar IDs.

**Prompt de refinamiento:**

> El frontend guarda userId como string en el JWT porque venía de MongoDB. Si los IDs son Integer en la base de datos nueva, las comparaciones van a fallar. Cámbialo para que los IDs sean UUID generados como strings con uuid.uuid4().

**Resultado:** La IA ajustó los modelos para usar `String(36)` como clave primaria y movió la generación del UUID al método `create()` de cada repositorio, que es donde tiene sentido hacerlo.

---

### Prompt 3 — Implementar la autenticación JWT como dependencias inyectables

**Contexto:** En el backend Node.js la autenticación eran dos funciones middleware encadenadas: `authenticateJWT` comprobaba el token y `isAdmin` verificaba el rol. Necesitaba replicar ese comportamiento en FastAPI, donde el mecanismo equivalente son las dependencias con `Depends()`.

**Prompt:**

> En Node.js tenía dos middlewares: uno que extrae el Bearer token del header Authorization, lo verifica con jsonwebtoken y mete el payload en req.user; y otro que comprueba que req.user.role sea admin. ¿Cómo hago lo mismo en FastAPI con Depends para poder proteger rutas individuales?

**Respuesta de la IA:** Generó dos funciones, `get_current_user` y `require_admin`, usando `HTTPBearer` de FastAPI para extraer el token del header y `Depends()` para encadenarlas.

**Problema detectado:** Cuando no se envía ningún token, el código devolvía 403 en vez de 401. El Node.js original devolvía 401 en ese caso. El frontend de Svelte distingue los dos códigos: 401 significa que la sesión ha expirado o no hay sesión, y redirige al login; 403 significa que hay sesión pero no tienes permisos, y muestra un error. Con 403 el usuario se quedaba bloqueado en la página sin ser redirigido.

**Prompt de refinamiento:**

> Cuando no hay token el servidor devuelve 403 pero el frontend espera 401 para redirigir al login. ¿Cómo consigo que la ausencia de token devuelva 401 y solo devuelva 403 cuando el token es válido pero el rol es insuficiente?

**Resultado:** Desactivar el error automático de `HTTPBearer` con `auto_error=False` y gestionar manualmente los dos casos: sin token o token inválido → 401, token válido pero sin rol admin → 403.

---

### Prompt 4 — Devolver `_id` en las respuestas JSON en vez de `id`

**Contexto:** El frontend Svelte accede a los recursos como `product._id` y `user._id` porque así los devolvía MongoDB. SQLAlchemy usa `id` como nombre de columna. Necesitaba que las respuestas JSON usaran `_id` sin tocar el frontend.

**Prompt:**

> Los modelos SQLAlchemy tienen una columna llamada `id` pero el frontend espera `_id` en el JSON, igual que hacía MongoDB. ¿Cómo consigo que los schemas Pydantic serialicen ese campo como `_id` en la respuesta?

**Respuesta de la IA:** Propuso usar `Field(alias="_id")` en el schema Pydantic junto con `populate_by_name=True` en el `model_config`.

**Problema detectado:** Tras aplicarlo, el JSON seguía devolviendo `id` en vez de `_id`. El alias estaba definido pero FastAPI no lo estaba usando al serializar.

**Prompt de refinamiento:**

> He puesto Field(alias='_id') y populate_by_name=True pero el JSON de respuesta sigue mostrando 'id'. ¿Qué está pasando?

**Respuesta:** El problema es que al construir la instancia del schema con `model_validate(orm_obj)`, Pydantic mapea por nombre de atributo (`id`), no por alias. Para que el alias funcione en la serialización hay que construir el objeto usando los kwargs con el alias directamente. La solución fue añadir un classmethod `from_orm_obj()` en cada schema que construye la instancia pasando explícitamente `_id=product.id`, `imageUrl=product.image_url`, etc.

---

### Prompt 5 — Manejadores globales de excepciones

**Contexto:** La práctica pide un manejador global de errores. Sin él, cada endpoint necesita su propio bloque try/except para convertir errores de base de datos o de lógica en respuestas HTTP, lo que duplica código y mezcla responsabilidades.

**Prompt:**

> Quiero definir excepciones propias de dominio como NotFoundError o ConflictError y que se traduzcan automáticamente a respuestas HTTP sin poner try/except en cada endpoint. ¿Cómo registro un manejador global en FastAPI?

**Respuesta de la IA:** Propuso el decorador `@app.exception_handler(NotFoundError)` en `main.py` con funciones async que devuelven un `JSONResponse` con el código y cuerpo correspondientes. También explicó que para los errores de validación de Pydantic hay que capturar `RequestValidationError` (la excepción interna de FastAPI), no `ValidationError` directamente. Correcto sin necesidad de iterar.

---

## 3. Análisis crítico: errores de la IA y correcciones manuales

---

### Error 1 — Incompatibilidad de versiones: passlib + bcrypt

**Código generado por la IA:**

```python
# core/security.py — versión con error
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

**El error al ejecutar:** Al hacer la primera petición de registro, el servidor lanzaba esto en tiempo de ejecución (no en importación, lo que lo hace más difícil de detectar):

```
(trapped) error reading bcrypt version
AttributeError: module 'bcrypt' has no attribute '__about__'
ValueError: password cannot be longer than 72 bytes, truncate manually
```

**Por qué ocurre:** passlib 1.7.4 (sin mantenimiento desde 2020) accede a `bcrypt.__about__.__version__` para detectar la versión del backend. bcrypt 4.x eliminó ese atributo. Al no poder leer la versión, passlib no ejecuta correctamente su lógica interna y la llamada a `hash()` falla.

**Por qué la IA lo recomendó:** Es el patrón de la documentación oficial de FastAPI, escrita cuando la combinación funcionaba. La IA reproduce lo que vio en su entrenamiento sin saber que passlib lleva años sin actualizarse. Es una alucinación por desfase temporal: código correcto para el ecosistema de 2021, roto en 2024+.

**Corrección aplicada:**

```python
# core/security.py — versión corregida
import bcrypt

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False
```

Se eliminó `passlib[bcrypt]==1.7.4` de `requirements.txt` y se añadió `bcrypt==4.2.1`. Eliminar el wrapper hace el código más legible y elimina una dependencia sin mantenimiento activo.

---

### Error 2 — Fallo de seguridad: escalada de privilegios en el registro

**Código generado por la IA:**

```python
# schemas/user.py — versión con error
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    role: UserRole = UserRole.user   # ← cualquier cliente puede enviar "admin"
```

```python
# services/auth_service.py — versión con error
def register(self, username, email, plain_password, role=UserRole.user):
    user = self._repo.create(username, email, plain_password, role)  # role viene del cliente
```

**El problema:** No hay ningún error en ejecución. La aplicación funciona perfectamente. El problema es que funciona de forma insegura: cualquier persona puede registrarse como administrador enviando `"role": "admin"` en el cuerpo de la petición.

**Demostración ejecutada durante el desarrollo:**

```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"atacante","email":"mal@example.com","password":"pass123","role":"admin"}'
```

Respuesta real del servidor con el código generado:

```json
{
  "message": "Usuario registrado",
  "user": {
    "username": "atacante",
    "email": "mal@example.com",
    "role": "admin"
  }
}
```

Un usuario anónimo tiene ahora acceso de administrador completo: puede crear, editar y borrar productos, listar todos los usuarios y cambiar roles. Sin haber tenido nunca ningún privilegio.

**Por qué la IA generó este código:** Estaba replicando la estructura del backend Node.js original, que también tenía `role` en el body del registro. La IA tomó ese diseño como referencia y lo trasladó sin analizar sus implicaciones de seguridad. Sabe perfectamente qué es la escalada de privilegios, pero no identificó el código de referencia como problemático: es un error de seguimiento acrítico del ejemplo de entrada.

Lo que lo hace especialmente peligroso es que no genera ningún log sospechoso. La petición llega como un registro normal, devuelve 201, y no hay ninguna señal de alerta.

Este tipo de vulnerabilidad se clasifica como **Broken Access Control** (OWASP Top 10 #1 desde 2021).

**Corrección aplicada:**

```python
# schemas/user.py — corregido
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    # 'role' eliminado: no se acepta nunca del cliente en el registro
```

```python
# services/auth_service.py — corregido
def register(self, username: str, email: str, plain_password: str) -> RegisterResponse:
    # El rol se fija aquí en la capa de servicio, nunca viene del exterior
    user = self._repo.create(username, email, plain_password, UserRole.user)
```

La promoción a administrador solo es posible mediante `PUT /api/users/{id}/role`, que requiere un token de administrador válido. El principio aplicado: el rol es una decisión del servidor, no una preferencia del cliente.

---

### Error 3 — Dos bugs de comportamiento HTTP: redirect que rompe la autenticación y código de estado incorrecto en token expirado

Este error es distinto a los anteriores porque no estaba en el código generado directamente, sino que emergió al conectar el frontend Svelte real con el backend. Los logs del servidor mostraban el problema con claridad:

```
GET /api/products HTTP/1.1   307 Temporary Redirect
GET /api/products/ HTTP/1.1  401 Unauthorized
GET /api/products HTTP/1.1   307 Temporary Redirect
GET /api/products/ HTTP/1.1  401 Unauthorized
GET /api/users/me HTTP/1.1   403 Forbidden    ← token expirado tratado como falta de permisos
```

Eran dos bugs distintos actuando a la vez.

#### Bug 3a — El redirect 307 descarta el header Authorization

**La causa en el código generado:**

FastAPI tiene `redirect_slashes=True` por defecto. El constructor de la aplicación generado por la IA era:

```python
# main.py — versión con error
app = FastAPI(title="Desert Vault API", version="2.0.0", docs_url="/api/docs")
# redirect_slashes=True por defecto
```

El frontend Svelte llama a `/api/products` (sin slash final, como hacía con el Node.js original). FastAPI detecta que la ruta registrada es `/api/products/` y emite un `307 Temporary Redirect`. El browser sigue el redirect automáticamente, pero **descarta el header `Authorization`** en la segunda petición. Este es el comportamiento estándar del API `fetch()`: por seguridad, no reenvía credenciales cuando se redirige. El servidor recibe la segunda petición sin token y devuelve 401. El resultado visible es el bucle que se ve en los logs: 307 → 401 → 307 → 401.

**Por qué la IA no lo detectó:** La IA generó el código en aislamiento, sin ejecutarlo contra el frontend real. En un test con `curl` o con un cliente HTTP que sigue redirects y reenvía headers, el problema no aparece. Solo surge cuando el browser hace la petición con `fetch()`, que tiene el comportamiento de seguridad de descartar credenciales en redirects.

**Corrección aplicada en `main.py`:**

```python
# main.py — corregido
app = FastAPI(
    title="Desert Vault API",
    version="2.0.0",
    docs_url="/api/docs",
    redirect_slashes=False,   # evita el 307 que descarta Authorization
)
```

Y en los routers, registrar explícitamente ambas variantes para que funcione con y sin slash:

```python
# routers/product_router.py — corregido
@router.get("", response_model=list[ProductResponse])
@router.get("/", response_model=list[ProductResponse], include_in_schema=False)
def list_products(...):
    ...
```

#### Bug 3b — Token expirado devuelve 403 en vez de 401

**La causa en el código generado:**

```python
# middleware/auth_middleware.py — versión con error
def _extract_token(credentials = Depends(bearer_scheme)) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Token no proporcionado.")
    try:
        return decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(
            status_code=403,   # ← incorrecto para token expirado
            detail="Token inválido o expirado."
        )
```

El frontend Svelte tiene esta lógica en `api.js`:

```javascript
// frontend/src/services/api.js
if (!res.ok) throw new Error(data.message || data.error || `HTTP ${res.status}`)
```

Y en los efectos de las páginas:

```javascript
// Si el token desaparece o la sesión expira → redirigir al login
$effect(() => {
    if (!authState.token) { navigate('login'); return; }
})
```

El problema es que ese efecto solo se activa cuando el token se borra del estado. Cuando el servidor devuelve 403, el frontend interpreta que hay permisos insuficientes (no que la sesión expiró), no borra el token, y el usuario se queda bloqueado: ve un error genérico en la página actual sin ser redirigido al login. El log `GET /api/users/me 403 Forbidden` era exactamente eso: un token expirado que el servidor respondía con 403, dejando al usuario colgado.

**Por qué la IA usó 403:** La lógica del 403 tiene sentido vista de forma aislada: "el token es inválido, por tanto el acceso está prohibido". Pero ignora la semántica HTTP correcta: 401 Unauthorized significa "no identificado o credenciales inválidas/expiradas", 403 Forbidden significa "identificado correctamente pero sin permisos suficientes". Un token expirado es un caso de 401, no de 403.

**Corrección aplicada:**

```python
# middleware/auth_middleware.py — corregido
def _extract_token(credentials = Depends(bearer_scheme)) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Token no proporcionado.")
    try:
        return decode_token(credentials.credentials)
    except JWTError:
        # Token expirado o inválido → 401, no 403.
        # El usuario necesita volver a autenticarse, no que se le diga que le faltan permisos.
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    # Solo llega aquí si el token es válido (401 ya gestionado arriba).
    # Token válido pero rol insuficiente → 403. Esto sí es correcto.
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requiere rol admin.")
    return current_user
```

La distinción queda clara: 401 para cualquier problema con las credenciales (ausente, expirada, malformada), 403 exclusivamente para credenciales válidas con rol insuficiente. Así el frontend puede actuar correctamente en cada caso.

---
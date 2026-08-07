# modulo-8

Take Home Challenge — Mentoría, Módulo 8. Sistema de gestión de notificaciones para usuarios autenticados: cada usuario puede crear, modificar, eliminar y consultar sus propias notificaciones, que se "envían" simulando pasos distintos según el canal (Email, SMS, Push).

## Features

- Registro de usuarios y login con JWT.
- Todos los endpoints (salvo registro y login) requieren token válido.
- CRUD completo de notificaciones: crear, modificar, eliminar, listar solo las propias.
- Al crear una notificación se ejecuta su "envío" simulado por el canal indicado (Email / SMS / Push), cada uno con su propia lógica.
- Un usuario no puede leer, modificar ni borrar notificaciones de otro (403 si lo intenta).
- Documentación interactiva en `/docs` (Swagger), con botón "Authorize" para loguearse y probar los endpoints protegidos directo desde ahí.

## Stack

- **Python 3.14** + **FastAPI**
- **SQLAlchemy 2.0** (async, `asyncpg`) + **PostgreSQL**
- **Alembic** para migraciones
- **PyJWT** + **bcrypt** para autenticación
- **Docker** / **Docker Compose**
- **pytest** + **httpx** + **anyio** para tests
- **ruff** para lint y formateo
- **uv** como gestor de paquetes

## Instalación y ejecución

Prerrequisito: tener **Docker** corriendo.

```bash
git clone https://github.com/victormarcias/modulo-8
cd modulo-8
cp .env.example .env
./run_project.sh
```

`run_project.sh` levanta Postgres y la API con Docker Compose, espera a que la base esté lista, y aplica las migraciones automáticamente. Al terminar:

- API: http://localhost:8000
- Docs (Swagger): http://localhost:8000/docs

## Tests

```bash
./run_tests.sh
./run_tests.sh -v          # verbose
./run_tests.sh -k users    # filtrar por nombre
```

Los tests corren contra una base de datos de test real (`modulo-8_test`), separada de la de desarrollo — no mockean la capa de persistencia, así que también cubren que las queries a la base funcionen de verdad. Se limpian solas entre cada test.

## Arquitectura

Clean Architecture, con las capas separadas por responsabilidad:

```
app/
├── routers/       # capa HTTP — recibe requests, valida con schemas, delega a service
├── service/       # lógica de negocio, sin dependencias de FastAPI ni SQL directo
├── repository/    # acceso a datos (SQLAlchemy)
├── client/        # envío por canal (Email/SMS/Push), Strategy pattern
├── models/        # entidades SQLAlchemy (persistencia)
├── schemas/       # contratos Pydantic (entrada/salida de la API)
├── database.py    # engine y sesión de SQLAlchemy
└── dependencies.py # dependencias de FastAPI compartidas (ej. get_current_user)
```

La regla de dependencia va hacia adentro: `routers` depende de `service`, `service` depende de `repository`/`client` (nunca al revés), y `service` no importa nada de FastAPI — es testeable llamándolo directo, sin levantar un server.

## Decisiones técnicas

- **`models/` y `schemas/` separados (no SQLModel).** Un solo modelo para DB y API mezclaría capas — por ejemplo, filtraría `password_hash` en las respuestas o permitiría mass assignment de campos que el cliente no debería poder setear.

- **Notificaciones por canal con Strategy pattern.** `NotificationSender` es la interfaz común; `EmailSender`, `SmsSender` y `PushSender` la implementan cada uno con su propia lógica. Agregar un canal nuevo es sumar una clase + una entrada en el registry, sin tocar los canales existentes.

- **Alembic corre con driver sync (`psycopg2`) aunque la app es async (`asyncpg`).** Las migraciones son un proceso batch que corre una sola vez por cambio de schema; no necesita ser async, y usar un engine sync ahí evita la complejidad de correr un loop async solo para eso.

- **Base de datos de test separada de la de desarrollo.** Permite correr tests contra Postgres real (no contra mocks del repositorio), sin arriesgar los datos que uno usa a mano mientras desarrolla.

- **`anyio` en vez de `pytest-asyncio`** para los tests async — es lo que recomienda la documentación oficial de FastAPI, y ya es dependencia transitiva de Starlette (no suma una librería nueva). Tener los dos plugins activos a la vez generaba conflictos de event loop.

- **Algoritmo JWT (`HS256`) hardcodeado, no configurable por variable de entorno.** El algoritmo no es secreto (viaja en el header del propio token, en texto plano), pero dejarlo fijo en código evita ataques de "algorithm confusion" — cualquier cambio pasa por code review, no por editar un `.env`.

- **Ownership check en notificaciones.** Aunque el enunciado solo pedía explícitamente que el listado devuelva "las propias", extendí la misma regla a consultar/modificar/eliminar por id — devuelven `403` si la notificación no pertenece al usuario del token.

- **`ruff` para lint y formateo.** Un solo tool en vez de `flake8` + `black` + `isort` por separado.

- **Contenedor de la app separado del de la base** (`docker-compose.yml` con servicios `db` y `app`), cada uno con su propio ciclo de vida.

## Endpoints principales

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/users/` | No | Registro de usuario |
| POST | `/auth/login` | No | Login, devuelve JWT |
| GET | `/users/` | Sí | Listar usuarios |
| GET | `/users/{id}` | Sí | Ver un usuario |
| POST | `/notifications/` | Sí | Crear notificación (dispara el envío) |
| GET | `/notifications/` | Sí | Listar las notificaciones propias |
| GET | `/notifications/{id}` | Sí | Ver una notificación propia |
| PUT | `/notifications/{id}` | Sí | Modificar una notificación propia |
| DELETE | `/notifications/{id}` | Sí | Eliminar una notificación propia |

Para los endpoints protegidos: usá el botón **Authorize** en `/docs` con tu email/password, o mandá el header `Authorization: Bearer <token>` a mano.

## Qué se podría mejorar

- Los datos de test (emails, passwords) están repetidos como literales en cada archivo, en vez de centralizados en `conftest.py`.
- No hay un script de seed para levantar la app con un usuario y notificaciones de ejemplo ya cargados.
- SMS y Push simulan el "número"/"device token" con el `user.id`, porque el modelo `User` no tiene esos campos todavía.
- Un solo rol de usuario — no hay permisos diferenciados (admin vs usuario común).
- El JWT no tiene refresh token — expira a los 60 minutos y hay que loguearse de nuevo.
- Pipeline de CI (lint + tests en cada push) todavía no está armado.
- Deployment a un hosting real quedó fuera del alcance de este challenge.

# modulo-8

Take Home Challenge — Mentorship, Module 8. Notification management system for authenticated users: each user can create, update, delete, and view their own notifications, which get "sent" simulating different steps depending on the channel (Email, SMS, Push).

## Features

- User registration and JWT login.
- All endpoints (except register and login) require a valid token.
- Full notification CRUD: create, update, delete, list only your own.
- Creating a notification triggers a simulated "send" through the specified channel (Email / SMS / Push), each with its own logic.
- A user cannot read, update, or delete another user's notifications (403 if attempted).
- Interactive documentation at `/docs` (Swagger), with an "Authorize" button to log in and try protected endpoints directly from there.

## Stack

- **Python 3.14** + **FastAPI**
- **SQLAlchemy 2.0** (async, `asyncpg`) + **PostgreSQL**
- **Alembic** for migrations
- **PyJWT** + **bcrypt** for authentication
- **Docker** / **Docker Compose**
- **pytest** + **httpx** + **anyio** for tests
- **ruff** for linting and formatting
- **uv** as package manager

## Installation and running it

Prerequisite: **Docker** running.

```bash
git clone https://github.com/victormarcias/modulo-8
cd modulo-8
cp .env.example .env
./run_project.sh
```

`run_project.sh` brings up Postgres and the API with Docker Compose, waits for the database to be ready, and applies migrations automatically. Once it finishes:

- API: http://localhost:8000
- Docs (Swagger): http://localhost:8000/docs

## Tests

```bash
./run_tests.sh
./run_tests.sh -v          # verbose
./run_tests.sh -k users    # filter by name
```

Tests run against a real test database (`modulo-8_test`), separate from the development one — they don't mock the persistence layer, so they also cover that queries against the database actually work. Tables are cleaned automatically between tests.

## Architecture

Clean Architecture, with layers separated by responsibility:

```
app/
├── routers/       # HTTP layer — receives requests, validates with schemas, delegates to service
├── service/       # business logic, no dependency on FastAPI or raw SQL
├── repository/    # data access (SQLAlchemy)
├── client/        # per-channel sending (Email/SMS/Push), Strategy pattern
├── models/        # SQLAlchemy entities (persistence)
├── schemas/       # Pydantic contracts (API input/output)
├── database.py    # SQLAlchemy engine and session
└── dependencies.py # shared FastAPI dependencies (e.g. get_current_user)
```

The dependency rule points inward: `routers` depends on `service`, `service` depends on `repository`/`client` (never the other way around), and `service` doesn't import anything from FastAPI — it's testable by calling it directly, without spinning up a server.

## Technical decisions

- **`models/` and `schemas/` kept separate (not SQLModel).** A single model for both DB and API would blur the layers — for example, it would leak `password_hash` in responses or allow mass assignment of fields the client shouldn't be able to set.

- **Notification channels via the Strategy pattern.** `NotificationSender` is the shared interface; `EmailSender`, `SmsSender`, and `PushSender` each implement it with their own logic. Adding a new channel means adding a class + one entry in the registry, without touching the existing channels.

- **Alembic runs with a sync driver (`psycopg2`) even though the app is async (`asyncpg`).** Migrations are a batch process that runs once per schema change; it doesn't need to be async, and using a sync engine there avoids the complexity of running an async loop just for that.

- **Separate test database from the development one.** Lets tests run against real Postgres (not against mocks of the repository layer), without risking the data used by hand during development.

- **`anyio` instead of `pytest-asyncio`** for async tests — it's what FastAPI's official documentation recommends, and it's already a transitive dependency of Starlette (no new library added). Having both plugins active at once caused event loop conflicts.

- **JWT algorithm (`HS256`) hardcoded, not configurable via environment variable.** The algorithm isn't a secret (it travels in plain text in the token's own header), but keeping it fixed in code prevents "algorithm confusion" attacks — any change goes through code review, not through editing a `.env`.

- **Ownership check on notifications.** Although the spec only explicitly required the listing to return "your own", I extended the same rule to viewing/updating/deleting by id — they return `403` if the notification doesn't belong to the token's user.

- **`ruff` for linting and formatting.** A single tool instead of `flake8` + `black` + `isort` separately.

- **App container separate from the database one** (`docker-compose.yml` with `db` and `app` services), each with its own lifecycle.

## Main endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/users/` | No | Register a user |
| POST | `/auth/login` | No | Login, returns a JWT |
| GET | `/users/` | Yes | List users |
| GET | `/users/{id}` | Yes | View a user |
| POST | `/notifications/` | Yes | Create a notification (triggers the send) |
| GET | `/notifications/` | Yes | List your own notifications |
| GET | `/notifications/{id}` | Yes | View one of your own notifications |
| PUT | `/notifications/{id}` | Yes | Update one of your own notifications |
| DELETE | `/notifications/{id}` | Yes | Delete one of your own notifications |

For protected endpoints: use the **Authorize** button in `/docs` with your email/password, or send the `Authorization: Bearer <token>` header manually.

## Areas to improve

- Test data (emails, passwords) is repeated as literals across test files instead of centralized in `conftest.py`.
- There's no seed script to bring the app up with a sample user and notifications already loaded.
- SMS and Push simulate the "phone number"/"device token" using `user.id`, since the `User` model doesn't have those fields yet.
- Single user role — no differentiated permissions (admin vs regular user).
- The JWT has no refresh token — it expires after 60 minutes and requires logging in again.
- CI pipeline (lint + tests on every push) isn't set up yet.
- Deployment to a real hosting provider was left out of scope for this challenge.

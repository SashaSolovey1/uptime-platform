# Uptime Platform

A self-hosted uptime monitoring and incident management platform built with FastAPI.

> **Status:** Early beta. The project is under active development.

## Current Features

- Monitor CRUD API
- Asynchronous HTTP checks
- Automatic monitor scheduling
- Check history stored in PostgreSQL
- HTTP status code and response time tracking
- Network error and timeout handling
- Monitor states: `pending`, `up`, `down`, `paused`
- Failure and recovery thresholds
- Automatic monitor state transitions
- Automatic incident creation and resolution
- Incidents API with status and monitor filtering
- Transactional outbox for incident events
- Separate notification worker
- Notification retry tracking
- Console notification channel
- Async SQLAlchemy repositories
- Alembic migrations
- Unit, API, and PostgreSQL integration tests

## Tech Stack

- Python 3.13
- FastAPI
- httpx2
- SQLAlchemy
- asyncpg
- PostgreSQL
- Alembic
- Pydantic
- asyncio
- Docker Compose
- pytest
- Ruff
- uv

## Getting Started

Clone the repository:

```bash
git clone https://github.com/SashaSolovey1/uptime-platform.git
cd uptime-platform
```

Install dependencies:

```bash
uv sync
```

Create the environment file:

```bash
cp .env.example .env
```

Start PostgreSQL:

```bash
make dev-up
```

Apply migrations:

```bash
make migrate
```

Start the API:

```bash
uv run fastapi dev src/uptime_platform/main.py
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Running Background Processes

Start the monitor scheduler:

```bash
make scheduler
```

Start the notification worker:

```bash
make notification-worker
```

For local development, the API, scheduler, and notification worker should run as separate processes.

## Development Commands

Start PostgreSQL:

```bash
make dev-up
```

Stop PostgreSQL:

```bash
make dev-down
```

Apply migrations:

```bash
make migrate
```

Run all tests:

```bash
make test
```

Run tests against a fresh test database:

```bash
make test-fresh
```

Run unit tests:

```bash
make test-unit
```

Run API tests:

```bash
make test-api
```

Run PostgreSQL integration tests:

```bash
make test-integration
```

Format code:

```bash
make format
```

Run lint checks:

```bash
make lint
```

Run the scheduler:

```bash
make scheduler
```

Run the notification worker:

```bash
make notification-worker
```

## Database Migrations

Create a migration:

```bash
uv run alembic revision --autogenerate -m "migration description"
```

Apply migrations:

```bash
make migrate
```

## Planned Features

- Safe outbox processing with multiple workers
- Notification retry backoff
- Webhook notifications
- Telegram notifications
- Email notifications
- Maintenance windows
- Public status pages
- TCP monitoring
- DNS monitoring
- TLS certificate monitoring
- Organizations
- RBAC
- API keys
- Audit log
- Prometheus metrics
- Grafana dashboards
- Redis-backed queues and distributed coordination
- Docker production setup
- CI/CD

## Version

`0.1.0-beta`
# Uptime Platform

A self-hosted uptime monitoring and incident management platform built with FastAPI.

> **Status:** Early beta. The project is under active development.

## Overview

Uptime Platform is a backend service for monitoring websites and services, storing check history, tracking availability, and eventually managing incidents, notifications, maintenance windows, and public status pages.

The project is being built as a modular monolith with clear separation between the API, application services, domain entities, persistence layer, and monitoring infrastructure.

## Current Features

- Monitor CRUD API
- Asynchronous HTTP availability checks
- HTTP status code tracking
- Response time measurement
- Network error and timeout handling
- Check history stored in PostgreSQL
- Async SQLAlchemy repositories
- Alembic database migrations
- Dependency injection with FastAPI
- Separate development and test PostgreSQL environments
- Unit tests
- API tests
- PostgreSQL integration tests
- Docker Compose development environment
- Makefile for common development commands

## Planned Features

- Automatic monitor scheduling
- Monitor state transitions
- Failure and recovery thresholds
- Incident creation and resolution
- Maintenance windows
- Notification channels
- Public status pages
- TCP monitoring
- DNS monitoring
- TLS certificate monitoring
- RBAC
- API keys
- Audit log
- Prometheus metrics

## Tech Stack

- Python 3.13
- FastAPI
- httpx2
- SQLAlchemy
- asyncpg
- PostgreSQL
- Alembic
- Pydantic
- Docker Compose
- pytest
- uv

## Project Structure

```text
src/uptime_platform/
├── checks/
│   ├── entities.py
│   ├── models.py
│   ├── protocols.py
│   ├── service.py
│   ├── sqlalchemy_repository.py
│   ├── dependencies.py
│   └── router.py
├── monitors/
│   ├── entities.py
│   ├── models.py
│   ├── schemas.py
│   ├── protocols.py
│   ├── service.py
│   ├── sqlalchemy_repository.py
│   ├── dependencies.py
│   └── router.py
├── db/
│   ├── base.py
│   └── session.py
└── main.py
```

## Requirements

You need the following installed:

- Python 3.13
- uv
- Docker
- Docker Compose
- make

## Getting Started

Clone the repository:

```bash
git clone https://github.com/SashaSolovey1/uptime-platform.git
cd uptime-platform
```

Install Python dependencies:

```bash
uv sync
```

Create the local environment file:

```bash
cp .env.example .env
```

Start the development PostgreSQL database:

```bash
make dev-up
```

Apply database migrations:

```bash
make migrate
```

Start the API:

```bash
uv run fastapi dev src/uptime_platform/main.py
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Testing

Run the complete test suite:

```bash
make test
```

Run only unit tests:

```bash
make test-unit
```

Run only API tests:

```bash
make test-api
```

Run PostgreSQL integration tests:

```bash
make test-integration
```

Run the complete test suite against a fresh test database:

```bash
make test-fresh
```

The integration tests use a separate temporary PostgreSQL instance and apply the same Alembic migrations used by the development and production environments.

## Database Migrations

Create a new migration:

```bash
uv run alembic revision --autogenerate -m "migration description"
```

Apply all migrations:

```bash
make migrate
```

## API Example

Create a monitor:

```bash
curl -X POST \
  http://127.0.0.1:8000/api/v1/monitors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example",
    "url": "https://example.com",
    "interval_seconds": 60,
    "timeout_seconds": 5
  }'
```

Run a check manually:

```bash
curl -X POST \
  http://127.0.0.1:8000/api/v1/monitors/<MONITOR_ID>/checks
```

Get check history:

```bash
curl \
  "http://127.0.0.1:8000/api/v1/monitors/<MONITOR_ID>/checks?limit=50"
```

## Development Status

The current version provides the basic foundation for the monitoring platform:

```text
Monitor
   ↓
HTTP Checker
   ↓
Check Result
   ↓
Check Service
   ↓
PostgreSQL
   ↓
Check History
```

Automatic scheduling, state transitions, incidents, and notifications are still under development.

## Version

`0.1.0-beta`
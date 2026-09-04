[![Docker Pulls](https://img.shields.io/docker/pulls/sashastudent/uptime-platform)](https://hub.docker.com/r/sashastudent/uptime-platform)
# Uptime Platform

A self-hosted uptime monitoring and incident management platform built with FastAPI.

> **Status:** MVP. The project is under active development.

## Current Features

- Monitor CRUD API
- Asynchronous HTTP checks
- Automatic monitor scheduling
- Configurable check intervals and timeouts
- Check history stored in PostgreSQL
- HTTP status code and response time tracking
- Network error and timeout handling
- Monitor states: `pending`, `up`, `down`, `paused`
- Failure and recovery thresholds
- Consecutive success and failure tracking
- Automatic monitor state transitions
- Automatic incident creation and resolution
- Incidents API with status and monitor filtering
- Transactional outbox for incident events
- Notification destinations configured through the API
- Multiple notification destinations
- Independent delivery state for each destination
- Separate notification worker
- PostgreSQL `FOR UPDATE SKIP LOCKED` worker claiming
- Lease-based delivery processing
- Notification retry with exponential backoff
- Webhook notification channel
- HMAC-SHA256 signed webhooks
- Webhook event IDs for idempotent receivers
- Async SQLAlchemy repositories
- Alembic migrations
- Unit, API, and PostgreSQL integration tests
- Maintenance windows configured through the API
- Monitoring continues during maintenance windows
- State transitions, incidents, and notifications are suppressed during maintenance

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

Apply database migrations:

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

## Background Processes

Start the monitor scheduler:

```bash
make scheduler
```

Start the notification worker:

```bash
make notification-worker
```

The API, scheduler, and notification worker run as separate processes.

## Notification Destinations

Notification destinations are stored in PostgreSQL and configured through the API.

Create a webhook destination:

```bash
curl -X POST \
  http://127.0.0.1:8000/api/v1/notification-destinations \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Production webhook",
    "destination_type": "webhook",
    "enabled": true,
    "webhook_url": "https://example.com/webhook",
    "webhook_secret": "change-this-secret"
  }'
```

The webhook secret is accepted when creating or updating a destination but is not returned by the API.

Each incident event is fanned out into an independent delivery for every enabled notification destination.

Webhook requests include:

```text
X-Uptime-Event-ID
X-Uptime-Timestamp
X-Uptime-Signature
```

The request body and timestamp are signed using HMAC-SHA256.

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

Run all tests against a fresh test database:

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

- Telegram notifications
- Email notifications
- Public status pages
- TCP monitoring
- DNS monitoring
- TLS certificate monitoring
- Organizations and projects
- RBAC
- API keys
- Audit log
- Prometheus metrics
- Grafana dashboards
- Redis-backed queues and distributed coordination
- Encrypted notification credentials
- Production Docker setup
- CI/CD

## Docker

The official container image is available on Docker Hub:

```bash
docker pull sashastudent/uptime-platform:0.1.0

## Version

`0.1.2`
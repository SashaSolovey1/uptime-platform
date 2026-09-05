[![Docker Pulls](https://img.shields.io/docker/pulls/sashastudent/uptime-platform)](https://hub.docker.com/r/sashastudent/uptime-platform)
# Uptime Platform

A self-hosted uptime monitoring and incident management platform built with FastAPI.

> **Status:** MVP. The project is under active development.

## Current Features

- HTTP uptime monitoring with configurable intervals and timeouts
- Automatic scheduling and check history
- Monitor states with failure and recovery thresholds
- Automatic incident creation and resolution
- Maintenance windows
- Public status pages
- Multiple notification destinations
- Webhook notifications with HMAC-SHA256 signatures
- Reliable notification delivery with retries
- Incident and monitoring APIs
- PostgreSQL persistence and Alembic migrations
- Unit, API, and PostgreSQL integration tests
- Docker Compose deployment
- Uptime statistics with 24h, 7d, 30d, and custom time ranges

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

## Monitor Statistics

Statistics are calculated from check history stored in PostgreSQL.

Available preset periods:

```text
24h
7d
30d

Example:
GET /api/v1/monitors/{monitor_id}/statistics?period=7d

Statistics include:

- uptime percentage
- total checks
- successful and failed checks
- average response time
```

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

- Telegram and email notifications
- TCP, DNS, and TLS certificate monitoring
- Organizations and projects
- RBAC and API keys
- Audit log
- Prometheus metrics and Grafana dashboards
- Redis-backed distributed coordination
- Encrypted notification credentials
- CI/CD

## Docker

The official container image is available on Docker Hub:

```bash
docker pull sashastudent/uptime-platform:latest
```
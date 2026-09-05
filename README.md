# Uptime Platform

[![Docker Pulls](https://img.shields.io/docker/pulls/sashastudent/uptime-platform)](https://hub.docker.com/r/sashastudent/uptime-platform)

Self-hosted uptime monitoring, incident management, and public status pages built with FastAPI.

> **Status:** MVP. The project is under active development.

## Features

- HTTP uptime monitoring with automatic scheduling and check history
- Automatic incident detection and recovery
- Maintenance windows
- Public status pages
- Uptime statistics with 24h, 7d, 30d, and custom time ranges
- Multiple webhook notification destinations
- Reliable notification delivery with retries and HMAC-SHA256 signatures
- PostgreSQL persistence with Alembic migrations
- Docker Compose deployment
- Unit, API, and PostgreSQL integration tests

## Quick Start

Clone the repository:

```bash
git clone https://github.com/SashaSolovey1/uptime-platform.git
cd uptime-platform
```

Create the environment file:

```bash
cp .env.example .env
```

Start the platform:

```bash
docker compose up -d
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Monitor Statistics

Get statistics for a preset period:

```text
GET /api/v1/monitors/{monitor_id}/statistics?period=7d
```

Or use a custom time range:

```text
GET /api/v1/monitors/{monitor_id}/statistics?starts_at=2026-09-01T00:00:00Z&ends_at=2026-09-05T00:00:00Z
```

Statistics include uptime percentage, check counts, and average response time.

## Notification Destinations

Webhook destinations are configured through the API.

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

Webhook requests are signed with HMAC-SHA256 and include event ID, timestamp, and signature headers.

## Development

Install dependencies:

```bash
uv sync
```

Start the development database:

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

Run the scheduler and notification worker in separate terminals:

```bash
make scheduler
make notification-worker
```

Run checks:

```bash
make format
make lint
make test-fresh
```

## Tech Stack

Python 3.13 · FastAPI · SQLAlchemy · PostgreSQL · asyncpg · Alembic · Pydantic · asyncio · Docker Compose · pytest · Ruff · uv

## Planned

- Telegram and email notifications
- TCP, DNS, and TLS certificate monitoring
- Organizations, RBAC, and API keys
- Prometheus metrics and Grafana dashboards
- Encrypted notification credentials
- CI/CD

## Docker

The official image is available on Docker Hub:

```bash
docker pull sashastudent/uptime-platform:latest
```

## License

Licensed under the [MIT License](LICENSE).
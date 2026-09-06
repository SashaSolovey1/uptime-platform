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
- Webhook and Telegram notification destinations
- Reliable notification delivery with retries
- HMAC-SHA256 signed webhook requests
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
make docker-up
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

Notification destinations are configured through the API.

### Webhook

```bash
curl -X POST \
  http://127.0.0.1:8000/api/v1/notification-destinations \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Production webhook",
    "destination_type": "webhook",
    "enabled": true,
    "config": {
      "url": "https://example.com/webhook",
      "secret": "change-this-secret"
    }
  }'
```

Webhook requests are signed with HMAC-SHA256 and include event ID, timestamp, and signature headers.

### Telegram

Create a bot with BotFather and obtain its bot token and target chat ID.

```bash
curl -X POST \
  http://127.0.0.1:8000/api/v1/notification-destinations \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Production Telegram",
    "destination_type": "telegram",
    "enabled": true,
    "config": {
      "bot_token": "your-bot-token",
      "chat_id": "your-chat-id"
    }
  }'
```

Telegram notifications are sent when incidents are opened or resolved.

Sensitive destination credentials are not returned by the API.

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

### Docker

Build the application image:

```bash
make docker-build
```

Start the full stack:

```bash
make docker-up
```

Show container status:

```bash
make docker-ps
```

Follow service logs:

```bash
make logs-api
make logs-scheduler
make logs-notification-worker
```

Stop and remove containers:

```bash
make docker-down
```

Rebuild the application from a clean database:

```bash
make docker-reset
```

> `make docker-reset` removes Docker volumes and deletes local PostgreSQL data.

## Tech Stack

Python 3.13 · FastAPI · SQLAlchemy · PostgreSQL · asyncpg · Alembic · Pydantic · asyncio · Docker Compose · pytest · Ruff · uv

## Planned

- Email notifications
- TCP, DNS, and TLS certificate monitoring
- Organizations, RBAC, and API keys
- Prometheus metrics and Grafana dashboards
- Encrypted notification credentials
- CI/CD

## Docker

The image is available on Docker Hub:

```bash
docker pull sashastudent/uptime-platform:latest
```

## License

Licensed under the [MIT License](LICENSE).
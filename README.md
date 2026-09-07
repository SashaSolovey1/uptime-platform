# Uptime Platform

[![Docker Pulls](https://img.shields.io/docker/pulls/sashastudent/uptime-platform)](https://hub.docker.com/r/sashastudent/uptime-platform)

Self-hosted uptime monitoring, incident management, and public status pages built with FastAPI.

> **Status:** MVP. The project is under active development.

## Features

- HTTP and TCP uptime monitoring with automatic scheduling and check history
- Typed monitor configurations for HTTP and TCP targets
- Automatic checker selection based on monitor type
- Serialized monitor state updates to prevent concurrent check races
- Automatic incident detection and recovery
- Maintenance windows
- Public status pages
- Uptime statistics with 24h, 7d, 30d, and custom time ranges
- Webhook, Telegram, and email notification destinations
- Reliable notification delivery with retries
- HMAC-SHA256 signed webhook requests
- SMTP email delivery with TLS and STARTTLS support
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

## API

The platform exposes a REST API for managing monitors, checks, incidents, maintenance windows, status pages, statistics, and notification destinations.

HTTP and TCP monitors use different configuration structures depending on the selected monitor type.

The current request and response schemas, available endpoints, validation rules, and example payloads can be found in the interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Monitor Statistics

Monitor statistics are available for 24h, 7d, 30d, and custom time ranges.

Statistics include uptime percentage, successful and failed check counts, total checks, and average response time.

See the Swagger documentation for the available statistics endpoints and request parameters.

## Notification Destinations

Notifications are sent when incidents are opened or resolved.

Supported notification destinations:

- Webhook
- Telegram
- Email

Webhook requests support HMAC-SHA256 signatures.

Email notifications are delivered through SMTP with the following security modes:

- `none`
- `starttls`
- `tls`

Sensitive destination credentials such as webhook secrets, Telegram bot tokens, and SMTP passwords are not returned by the API.

See the Swagger documentation for notification destination configuration and request schemas.

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

Rebuild the application containers while preserving the database:

```bash
make docker-rebuild
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

Python 3.13 · FastAPI · SQLAlchemy · PostgreSQL · asyncpg · Alembic · Pydantic · asyncio · httpx2 · aiosmtplib · Docker Compose · pytest · Ruff · uv

## Planned

- DNS and TLS certificate monitoring
- Organizations, RBAC, and API keys
- Prometheus metrics and Grafana dashboards
- Encrypted notification credentials
- CI/CD

## Docker

The image is available on Docker Hub:

```bash
docker pull sashastudent/uptime-platform:latest
```

Versioned images are also available:

```bash
docker pull sashastudent/uptime-platform:0.6.0
```

## License

Licensed under the [MIT License](LICENSE).
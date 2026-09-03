FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync \
    --frozen \
    --no-dev \
    --no-install-project

COPY . .

RUN uv sync \
    --frozen \
    --no-dev

ENV PATH="/app/.venv/bin:$PATH"

LABEL org.opencontainers.image.title="Uptime Platform"
LABEL org.opencontainers.image.description="Self-hosted uptime monitoring and incident management platform"
LABEL org.opencontainers.image.source="https://github.com/SashaSolovey1/uptime-platform"

CMD ["fastapi", "run", "src/uptime_platform/main.py", "--host", "0.0.0.0", "--port", "8000"]
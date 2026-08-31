.PHONY: \
	dev-up \
	dev-down \
	migrate \
	test-db-up \
	test-db-down \
	test-migrate \
	test \
	test-unit \
	test-api \
	test-integration \
	test-fresh
	lint
	format
	scheduler


dev-up:
	docker compose up -d --wait postgres


dev-down:
	docker compose stop postgres


migrate:
	uv run alembic upgrade head


test-db-up:
	docker compose --profile test up -d --wait postgres-test


test-db-down:
	docker compose --profile test rm -sf postgres-test


test-migrate: test-db-up
	set -a; . ./.env.test; set +a; uv run alembic upgrade head


test-unit:
	uv run pytest tests/unit -v


test-api:
	uv run pytest tests/api -v


test-integration: test-migrate
	uv run pytest tests/integration -v


test: test-migrate
	uv run pytest -v


test-fresh:
	docker compose --profile test rm -sf postgres-test
	$(MAKE) test

format:
	uv run ruff format .
	uv run ruff check --fix .


lint:
	uv run ruff format --check .
	uv run ruff check .

scheduler:
	uv run python -m uptime_platform.scheduler.main
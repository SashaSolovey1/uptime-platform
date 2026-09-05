# Contributing

Contributions are welcome.

## Development Setup

Clone the repository and install dependencies:

```bash
uv sync
cp .env.example .env
make dev-up
make migrate
```

Before submitting a pull request:

```bash
make format
make lint
make test-fresh
```

## Pull Requests

Keep changes focused and describe what was changed and why.

Commit prefixes used in the project:

- `feat:` new functionality
- `fix:` bug fixes
- `refactor:` internal changes
- `test:` tests
- `docs:` documentation
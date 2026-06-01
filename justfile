default:
    just --list

install:
    uv sync

test:
    uv run pytest

lint:
    uv run ruff check .

format:
    uv run black .
    uv run ruff format .


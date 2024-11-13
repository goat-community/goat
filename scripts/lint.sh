#!/usr/bin/env bash

set -e
set -x

uv run ruff check .
uv run ruff format . --check

pnpm run lint

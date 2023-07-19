#!/usr/bin/env bash

set -e
set -x

poetry run ruff src tests 
poetry run black --check src tests
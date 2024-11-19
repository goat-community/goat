FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1
WORKDIR /app/
# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.5.1 /uv /bin/uv

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/app/.venv/bin:$PATH"

# - compilte byte-compile packages for faster application startups,
# - silence uv complaining about not being able to use hard links,
# - prevent uv from accidentally downloading isolated Python builds,
# - Pick a Python (use `/usr/bin/python3.12` on uv 0.5.0 and later),
# - declare `/app` as the target for `uv sync`.
# @Ref: https://docs.astral.sh/uv/guides/integration/docker
# @Ref: https://docs.astral.sh/uv/reference/cli/#uv-sync
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-install-project --no-install-workspace

COPY ./pyproject.toml ./uv.lock /app/

COPY apps/geoapi /app/apps/geoapi

RUN --mount=type=cache,target=/root/.cache/uv \
     uv sync --frozen --no-dev --no-editable --package=geoapi

CMD ["fastapi", "run", "apps/geoapi/src/geoapi/main.py"]

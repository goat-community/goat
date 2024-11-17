FROM python:3.12-bookworm

WORKDIR /app

# Update debian
RUN apt-get update
RUN apt-get upgrade -y

# Install general required dependencies
RUN apt-get install --no-install-recommends -y tzdata ca-certificates curl wget git build-essential

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.5.1 /uv /bin/uv
ENV PYTHONPATH=/app/.venv/bin/python \
    UV_PYTHON=python3.12 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Install Node.js
ENV NVM_DIR /usr/local/nvm
RUN mkdir -p $NVM_DIR
ENV NODE_VERSION 20.15.0
RUN curl --silent -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default

ENV PNPM_VERSION 9.5.0
RUN wget -qO- https://get.pnpm.io/install.sh | ENV="$HOME/.bashrc" SHELL="$(which bash)" bash -

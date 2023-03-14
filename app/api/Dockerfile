FROM python:3.9-bullseye
# create directory for the app user
RUN mkdir -p /app
WORKDIR /app/
# Create the app user
#RUN addgroup --system app && adduser --system --group app
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT prod
ENV PYTHONPATH "${PYTHONPATH}:."
ENV USE_PYGEOS 0
# Install system dependencies
RUN apt-get update \
    && apt-get -y install netcat gcc libpq-dev \
    && apt-get clean
# Install postgresql-client
RUN apt install curl ca-certificates gnupg -y && \
    curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/apt.postgresql.org.gpg >/dev/null && \
    sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main" > /etc/apt/sources.list.d/postgresql.list' && \
    apt update -y && apt-get install postgresql-client-14 -y
# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Download Celery daemon
RUN curl -sSL https://raw.githubusercontent.com/celery/celery/master/extra/generic-init.d/celeryd > /etc/init.d/celeryd && \
    chmod +x /etc/init.d/celeryd

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/
# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'True' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"
COPY . /app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]

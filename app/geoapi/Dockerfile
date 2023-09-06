FROM python:3.11.4-bullseye
# create directory for the api user
RUN mkdir -p /api
WORKDIR /api/

# Install system dependencies
RUN apt-get update \
    && apt-get clean

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /api/
# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"
COPY . /api
ENV PYTHONPATH "${PYTHONPATH}:/api"
ENV PYDEVD_DISABLE_FILE_VALIDATION=1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]

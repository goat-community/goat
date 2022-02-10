FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app/

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'True' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

# Allow installing C++ GDP for debugging
ARG INSTALL_GDB=false
RUN bash -c "if [ $INSTALL_GDB == 'True' ] ; then apt-get update && apt-get -y install build-essential gdb && apt-get -y install cmake; fi"

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG INSTALL_JUPYTER=false
RUN bash -c "if [ $INSTALL_JUPYTER == 'True' ] ; then pip install jupyterlab ; fi"

COPY . /app
ENV PYTHONPATH=/app
ENV MODULE_NAME="src.main"


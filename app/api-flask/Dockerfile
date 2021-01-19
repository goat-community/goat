FROM python:3.9-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY *-requires.txt ./

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip setuptools \
    && pip install --user --no-cache-dir --no-warn-script-location -r requirements.txt

ENV PYTHONUNBUFFERED 1
ENV PATH $PATH:/root/.local/bin
ENV FLASK_APP src/app.py
ENV FLASK_ENV production

COPY ./ ./

EXPOSE 5000

CMD python src/app.py

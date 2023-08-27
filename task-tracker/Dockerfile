FROM docker-public.sberned.ru/python:3.11.3-bullseye

WORKDIR /app

RUN pip install -U pip
RUN pip3 install poetry==1.4.2
COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . /app

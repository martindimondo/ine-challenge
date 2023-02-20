FROM python:3.10-slim as builder

ENV POETRY_VERSION=1.3.2

WORKDIR /app
COPY poetry.lock pyproject.toml  ./

RUN python -m pip install --upgrade pip

RUN pip install "poetry==$POETRY_VERSION"

RUN apt update
RUN apt install -y postgresql-client gcc python3-dev musl-dev

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

COPY . .

RUN poetry run python manage.py migrate
RUN poetry run black --check .
RUN poetry run pylint **/*.py
RUN poetry run coverage run -m --source=. pytest .
RUN poetry run coverage report

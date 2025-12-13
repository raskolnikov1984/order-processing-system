FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apt-get update \
    && pip install --no-cache-dir poetry \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-ansi && rm -rf $POETRY_CACHE_DIR

COPY ./tests ./tests
COPY ./src ./src

EXPOSE 8010
CMD ["uvicorn", "src.order_service.main:app", "--host", "0.0.0.0", "--port", "8010"]

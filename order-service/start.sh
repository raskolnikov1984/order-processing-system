#!/usr/bin/env sh
alembic revision --autogenerate -m 'Initial Tables'
alembic upgrade head
uvicorn src.order_service.main:app --host 0.0.0.0 --port 8010 --reload

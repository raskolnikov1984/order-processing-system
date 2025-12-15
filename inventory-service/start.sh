#!/usr/bin/env sh
alembic upgrade head
uvicorn src.inventory_service.main:app --host 0.0.0.0 --port 8010 --reload

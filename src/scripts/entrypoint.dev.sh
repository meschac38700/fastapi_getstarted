#!/bin/bash

alembic upgrade head

fastapi dev main.py --app=app --host="${APP_HOST:-0.0.0.0}" --port="${APP_PORT:-80}"

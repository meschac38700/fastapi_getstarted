#!/bin/bash

# Remove unused file copied for test environment
rm -rf tox.ini

alembic upgrade head

fastapi run main.py --app=app --host="${APP_HOST:-0.0.0.0}" --port="${APP_PORT:-80}"

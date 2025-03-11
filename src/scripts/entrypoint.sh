#!/bin/bash

# Remove unused file copied for test environment
rm -rf tox.ini

# shellcheck disable=SC1009
until alembic upgrade head 2> /dev/null;
do
  sleep 2
  echo "Try apply migrations again.."
done

fastapi run main.py --app=app --host="${APP_HOST:-0.0.0.0}" --port="${APP_PORT:-80}"

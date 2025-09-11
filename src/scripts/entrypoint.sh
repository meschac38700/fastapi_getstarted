#!/bin/bash

# shellcheck disable=SC1009
until alembic upgrade head 2> /dev/null;
do
  sleep 2
  echo "Retry running migrations.."
done

fastapi run --entrypoint main:app --host="${APP_HOST:-0.0.0.0}" --port="${APP_PORT:-80}"

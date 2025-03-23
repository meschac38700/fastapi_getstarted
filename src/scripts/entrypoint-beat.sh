#!/bin/bash

# shellcheck disable=SC1009
until alembic upgrade head 2> /dev/null;
do
  sleep 2
  echo "Retry running migrations.."
done

celery -A main.celery beat --loglevel="${CELERY_LOG_LEVEL:-INFO}"

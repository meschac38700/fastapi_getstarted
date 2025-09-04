#!/bin/bash

echo "Running migrations"

cd src || true
alembic upgrade head
cd - || true

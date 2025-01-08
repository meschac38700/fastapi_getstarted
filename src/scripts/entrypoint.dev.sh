#!/bin/bash

alembic upgrade head

# fix pythonpath pytest config
echo """[pytest]
python_files = tests.py test_*.py *_tests.py
testpaths =
    src/tests
addopts = --rootdir ./src
pythonpath = .
asyncio_mode=auto
asyncio_default_fixture_loop_scope=function
""" > tox.ini

fastapi dev main.py --app=app --host="${APP_HOST:-0.0.0.0}" --port="${APP_PORT:-80}"

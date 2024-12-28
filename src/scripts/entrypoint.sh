#!/bin/bash

fastapi run main.py --app=app --host="${APP_HOST:-0.0.0.0}" --port="${APP_PORT:-80}"

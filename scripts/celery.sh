#!/usr/bin/sh

poetry run celery --app agir.api flower --port=80 &
poetry run celery --app agir.api worker --concurrency=2 -Q celery

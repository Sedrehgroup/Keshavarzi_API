#!/bin/bash

set -e

python manage.py wait_for_db
python manage.py wait_for_celery

python manage.py makemigrations --noinput
python manage.py migrate
python manage.py collectstatic --no-input

python manage.py geoserver_startup

gunicorn --reload config.wsgi --bind 0.0.0.0:8000

#!/bin/bash

set -e

python manage.py makemigrations --noinput
python manage.py migrate
python manage.py collectstatic --no-input
gunicorn --reload config.wsgi --bind 0.0.0.0:8000

python manage.py geoserver_startup
#!/bin/bash

#https://www.gnu.org/software/bash/manual/bash.html#The-Set-Builtin
set -e

celery -A config beat -l DEBUG -f logs/beat.log --scheduler django_celery_beat.schedulers:DatabaseScheduler --detach

python manage.py wait_for_db
python manage.py wait_for_celery

python manage.py makemigrations --noinput
python manage.py migrate
# python manage.py collectstatic --no-input

python manage.py geoserver_startup

figlet sedreh AI

gunicorn --reload config.wsgi --bind 0.0.0.0:8000

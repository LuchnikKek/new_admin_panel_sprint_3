#!/usr/bin/env bash

export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_PASSWORD=123123
export DJANGO_SUPERUSER_EMAIL=mail@mail.ru

python manage.py migrate --noinput
python manage.py createsuperuser --noinput || true

uwsgi --strict --ini /opt/app/uwsgi.ini
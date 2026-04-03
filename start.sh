#!/usr/bin/env bash
set -e

python manage.py migrate --run-syncdb --verbosity=0
python manage.py sync_users --verbosity=0
python manage.py collectstatic --noinput --verbosity=0

exec gunicorn barbershop.wsgi:application \
    --bind 0.0.0.0:5000 \
    --workers 2 \
    --timeout 60 \
    --log-level info

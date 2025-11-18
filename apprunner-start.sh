#!/bin/bash
set -e

# Migraciones para django-tenants
python manage.py migrate_schemas --shared
python manage.py migrate_schemas --tenant

# Static
python manage.py collectstatic --noinput

# Arrancar Gunicorn
gunicorn --bind 0.0.0.0:${PORT:-8000} config.wsgi:application

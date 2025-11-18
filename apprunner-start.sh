#!/bin/bash
set -e

# Migraciones para django-tenants
python3 manage.py migrate_schemas --shared
python3 manage.py migrate_schemas --tenant

# Static
#python3 manage.py collectstatic --noinput

# Arrancar Gunicorn
gunicorn --bind 0.0.0.0:${PORT:-8000} config.wsgi:application

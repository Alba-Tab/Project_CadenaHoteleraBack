#!/bin/bash
set -e

echo "=== DIAGNÓSTICO DE PAQUETES INSTALADOS ==="
pip list
echo "=== FIN DIAGNÓSTICO ==="
# Migraciones para django-tenants
python3 manage.py migrate_schemas --shared
python3 manage.py migrate_schemas --tenant

# Static
#python3 manage.py collectstatic --noinput

# Arrancar Gunicorn
python3 -m gunicorn --bind 0.0.0.0:${PORT:-8000} config.wsgi:application

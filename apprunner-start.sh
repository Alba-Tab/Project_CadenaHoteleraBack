#!/bin/bash
set -e

echo "=== INICIANDO SCRIPT ==="
# Verificamos si Django llegó vivo
pip3 list | grep Django

# Migraciones
python3 manage.py migrate_schemas --shared
python3 manage.py migrate_schemas --tenant

# Arrancar Gunicorn
echo "=== INICIANDO SERVIDOR ==="
python3 -m gunicorn --bind 0.0.0.0:${PORT:-8000} config.wsgi:application

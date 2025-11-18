#!/bin/bash
set -e

echo "=== VERIFICANDO INSTALACION ==="
# Ahora esto SÍ debería mostrar Django
pip3 list | grep Django

# Migraciones
python3 manage.py migrate_schemas --shared
python3 manage.py migrate_schemas --tenant

# Arrancar Gunicorn (COMO MÓDULO)
echo "=== INICIANDO SERVIDOR ==="
python3 -m gunicorn --bind 0.0.0.0:${PORT:-8000} config.wsgi:application

#!/bin/bash
set -e

echo "=== DIAGNÓSTICO ==="
echo "Directorio actual:"
pwd
echo "Listando carpetas clave (deberíamos ver 'django' aquí):"
ls -d django || echo "OJO: No veo la carpeta django"

echo "=== EJECUTANDO MIGRACIONES ==="
python3 manage.py migrate_schemas --shared
python3 manage.py migrate_schemas --tenant

echo "=== INICIALIZANDO DATOS ==="
python3 init_app.py

echo "=== INICIANDO SERVIDOR ==="
python3 -m gunicorn --bind 0.0.0.0:${PORT:-8000} config.wsgi:application
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    config.wsgi:application

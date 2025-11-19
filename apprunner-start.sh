#!/bin/bash
set -e

# 1. AGREGAR LA CARPETA ACTUAL AL PATH DE PYTHON (CRÍTICO)
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "=== DIAGNÓSTICO ==="
echo "Directorio actual:"
pwd
echo "Listando carpetas clave (deberíamos ver 'django' aquí):"
ls -d django || echo "OJO: No veo la carpeta django"

# 2. Migraciones
echo "=== EJECUTANDO MIGRACIONES ==="
python3 manage.py migrate_schemas --shared
python3 manage.py migrate_schemas --tenant

# 3. Arrancar Gunicorn
echo "=== INICIANDO SERVIDOR ==="
# Usamos python3 -m para asegurarnos de que usa el gunicorn local
python3 -m gunicorn --bind 0.0.0.0:${PORT:-8000} config.wsgi:application

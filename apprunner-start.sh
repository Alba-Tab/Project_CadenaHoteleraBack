#!/bin/bash
set -e

echo "=== DIAGNÓSTICO RÁPIDO ==="
# Usamos pip3 explícitamente
pip3 list | grep Django
echo "=== FIN DIAGNÓSTICO ==="

# Migraciones (usando python3)
python3 manage.py migrate_schemas --shared
python3 manage.py migrate_schemas --tenant

# Estáticos (Descomenta esto cuando arregles el STATIC_ROOT en settings.py)
# python3 manage.py collectstatic --noinput

# Arrancar Gunicorn (usando python3 -m para evitar error de ruta)
echo "=== INICIANDO SERVIDOR ==="
python3 -m gunicorn --bind 0.0.0.0:${PORT:-8000} config.wsgi:application

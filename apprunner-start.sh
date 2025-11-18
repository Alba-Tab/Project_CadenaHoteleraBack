#!/bin/bash
set -e

echo "=== FORZANDO INSTALACIÓN DE DEPENDENCIAS ==="
# FORZAR LA INSTALACIÓN AQUÍ MISMO
pip3 install -r requirements.txt
echo "=== INSTALACIÓN COMPLETADA ==="

echo "=== VERIFICACIÓN ==="
pip3 list | grep Django
echo "=== FIN VERIFICACIÓN ==="

# Migraciones
python3 manage.py migrate_schemas --shared
python3 manage.py migrate_schemas --tenant

# Estáticos (recuerda configurar STATIC_ROOT en settings.py antes de descomentar)
# python3 manage.py collectstatic --noinput

# Arrancar Gunicorn
echo "=== INICIANDO GUNICORN ==="
python3 -m gunicorn --bind 0.0.0.0:${PORT:-8000} config.wsgi:application

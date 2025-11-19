#!/bin/bash
set -e

# Configurar PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "=== DIAGNÓSTICO ==="
echo "Directorio actual: $(pwd)"
echo "Python version: $(python3 --version)"

# Migraciones
echo "=== EJECUTANDO MIGRACIONES ==="
python3 manage.py migrate_schemas --shared
python3 manage.py migrate_schemas --tenant

# Crear tenant público automáticamente
echo "=== CONFIGURANDO TENANT PÚBLICO ==="
python3 create_public_tenant.py || echo "Warning: No se pudo crear tenant público"

# Arrancar Gunicorn
echo "=== INICIANDO SERVIDOR ==="
exec gunicorn \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    config.wsgi:application

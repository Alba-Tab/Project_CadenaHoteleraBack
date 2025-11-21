"""
URLs principales - Django Tenants determina automáticamente qué URLconf usar:
- Si connection.schema_name == 'public': usa PUBLIC_SCHEMA_URLCONF
- Si connection.schema_name != 'public': usa TENANT_URLCONF

Este archivo se usa como fallback/base para ambos contextos.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Incluir rutas comunes si es necesario
]

"""
Script para crear usuario administrador en el esquema público
Ejecutar con: python manage.py shell < crear_admin_public.py
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django_tenants.utils import schema_context

with schema_context("public"):
    # Verificar si ya existe
    if User.objects.filter(username='admin').exists():
        print("✅ Usuario 'admin' ya existe")
        user = User.objects.get(username='admin')
        # Asegurar que sea staff y superuser
        if not user.is_staff or not user.is_superuser:
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print("✅ Usuario 'admin' actualizado como staff y superuser")
    else:
        # Crear superusuario
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("✅ Superusuario 'admin' creado exitosamente")
        print("   Usuario: admin")
        print("   Password: admin123")
        print("   Email: admin@example.com")

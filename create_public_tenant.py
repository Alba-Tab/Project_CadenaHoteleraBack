#!/usr/bin/env python
"""
Script para crear tenant público y domain localhost
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Tenant, Domain

def create_public_tenant():
    try:
        # Crear tenant público
        public_tenant, created = Tenant.objects.get_or_create(
            schema_name='public',
            defaults={'name': 'Public Schema'}
        )
        
        if created:
            print("✅ Tenant público creado")
        else:
            print("✅ Tenant público ya existe")
        
        # Crear domain para localhost
        domain, created = Domain.objects.get_or_create(
            domain='localhost',
            defaults={'tenant': public_tenant, 'is_primary': True}
        )
        
        if created:
            print("✅ Domain creado: localhost -> public")
        else:
            print("✅ Domain ya existe: localhost -> public")
            
        print("\n🎉 Configuración completada!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    create_public_tenant()
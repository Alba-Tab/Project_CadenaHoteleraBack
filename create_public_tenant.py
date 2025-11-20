"""
Script para crear el tenant público en AWS App Runner
Ejecutar después de las migraciones
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Tenant

def create_public_tenant():
    """Crea el tenant público si no existe"""
    
    # Dominio de App Runner (cámbialo por tu dominio real)
    app_runner_domain = os.getenv('APP_RUNNER_DOMAIN', 'jgyqzmxg7p.us-east-2.awsapprunner.com')
    
    print(f"🔍 Verificando tenant público para dominio: {app_runner_domain}")
    
    # Verificar si ya existe
    if Domain.objects.filter(domain=app_runner_domain).exists():
        print(f"✅ El dominio {app_runner_domain} ya existe")
        return
    
    # Crear tenant público
    try:
        tenant, created = Tenant.objects.get_or_create(
            schema_name='public',
            defaults={
                'name': 'Public Tenant',
                'paid_until': None,
                'on_trial': False
            }
        )
        
        if created:
            print(f"✅ Tenant público creado: {tenant.name}")
        else:
            print(f"ℹ️  Tenant público ya existía: {tenant.name}")
        
        # Crear dominio
        domain, created = Domain.objects.get_or_create(
            domain=app_runner_domain,
            defaults={'tenant': tenant, 'is_primary': True}
        )
        
        if created:
            print(f"✅ Dominio creado: {domain.domain}")
        else:
            print(f"ℹ️  Dominio ya existía: {domain.domain}")
            
        # También agregar localhost para desarrollo
        localhost_domain, created = Domain.objects.get_or_create(
            domain='localhost',
            defaults={'tenant': tenant, 'is_primary': False}
        )
        
        if created:
            print(f"✅ Dominio localhost creado")
        
        print("\n🎉 Tenant público configurado correctamente")
        
    except Exception as e:
        print(f"❌ Error al crear tenant público: {e}")
        raise

if __name__ == '__main__':
    create_public_tenant()

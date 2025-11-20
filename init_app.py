"""
Script de inicialización automática para App Runner
Crea el tenant público y los planes de suscripción
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Tenant, Domain
from apps.suscripciones.models import Plan

def crear_tenant_publico():
    """Crea el tenant público si no existe"""
    print("Verificando tenant público...")
    
    if Tenant.objects.filter(schema_name='public').exists():
        print("✅ Tenant público ya existe")
        return Tenant.objects.get(schema_name='public')
    
    print("Creando tenant público...")
    tenant = Tenant(
        schema_name='public',
        name='Public Schema',
        on_trial=False
    )
    tenant.save()
    print("✅ Tenant público creado")
    
    # Crear dominios por defecto
    dominios = ['localhost', 'jgyqzmxg7p.us-east-2.awsapprunner.com']
    for dominio in dominios:
        if not Domain.objects.filter(domain=dominio).exists():
            Domain.objects.create(
                domain=dominio,
                tenant=tenant,
                is_primary=(dominio == 'localhost')
            )
            print(f"✅ Dominio {dominio} creado")
    
    return tenant

def crear_planes():
    """Crea los planes de suscripción si no existen"""
    print("\nVerificando planes de suscripción...")
    
    planes_config = [
        # Plan Básico - Mensual
        {
            'nombre': 'Básico',
            'tipo': 'Mensual',
            'precio': 29.99,
            'max_usuarios': 5,
            'max_hoteles': 1
        },
        {
            'nombre': 'Básico',
            'tipo': 'Anual',
            'precio': 299.99,
            'max_usuarios': 5,
            'max_hoteles': 1
        },
        
        # Plan Profesional - Mensual/Anual/Trimestral
        {
            'nombre': 'Profesional',
            'tipo': 'Mensual',
            'precio': 79.99,
            'max_usuarios': 20,
            'max_hoteles': 3
        },
        {
            'nombre': 'Profesional',
            'tipo': 'Trimestral',
            'precio': 219.99,
            'max_usuarios': 20,
            'max_hoteles': 3
        },
        {
            'nombre': 'Profesional',
            'tipo': 'Anual',
            'precio': 799.99,
            'max_usuarios': 20,
            'max_hoteles': 3
        },
        
        # Plan Empresarial - Mensual/Anual
        {
            'nombre': 'Empresarial',
            'tipo': 'Mensual',
            'precio': 199.99,
            'max_usuarios': 100,
            'max_hoteles': 10
        },
        {
            'nombre': 'Empresarial',
            'tipo': 'Anual',
            'precio': 1999.99,
            'max_usuarios': 100,
            'max_hoteles': 10
        },
    ]
    
    creados = 0
    for config in planes_config:
        plan, created = Plan.objects.get_or_create(
            nombre=config['nombre'],
            tipo=config['tipo'],
            defaults={
                'precio': config['precio'],
                'max_usuarios': config['max_usuarios'],
                'max_hoteles': config['max_hoteles'],
                'activo': True
            }
        )
        
        if created:
            print(f"✅ Plan creado: {plan.nombre} - {plan.tipo} (${plan.precio})")
            creados += 1
        else:
            print(f"   Plan existe: {plan.nombre} - {plan.tipo}")
    
    if creados == 0:
        print("✅ Todos los planes ya existían")
    else:
        print(f"✅ {creados} planes nuevos creados")
    
    return Plan.objects.count()

def main():
    print("=" * 60)
    print("INICIALIZANDO APLICACIÓN")
    print("=" * 60)
    
    try:
        # 1. Crear tenant público
        crear_tenant_publico()
        
        # 2. Crear planes
        total_planes = crear_planes()
        
        print("\n" + "=" * 60)
        print("INICIALIZACIÓN COMPLETADA")
        print("=" * 60)
        print(f"Total de planes en el sistema: {total_planes}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    main()

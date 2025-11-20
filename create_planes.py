"""
Script para crear planes de suscripción

Ejecutar desde la raíz del proyecto:
    python create_planes.py
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.suscripciones.models import Plan, TipoChoices

def crear_planes():
    """Crea 3 planes con 3 variantes cada uno (Mensual, Trimestral, Anual)"""
    
    planes_data = [
        # PLAN BÁSICO
        {
            'nombre': 'Básico',
            'max_usuarios': 5,
            'max_hoteles': 1,
            'variantes': {
                TipoChoices.MENSUAL: 29.99,
                TipoChoices.TRIMESTRAL: 79.99,  # ~10% descuento
                TipoChoices.ANUAL: 299.99,       # ~17% descuento
            }
        },
        # PLAN PROFESIONAL
        {
            'nombre': 'Profesional',
            'max_usuarios': 20,
            'max_hoteles': 5,
            'variantes': {
                TipoChoices.MENSUAL: 79.99,
                TipoChoices.TRIMESTRAL: 219.99,  # ~8% descuento
                TipoChoices.ANUAL: 799.99,       # ~17% descuento
            }
        },
        # PLAN EMPRESARIAL
        {
            'nombre': 'Empresarial',
            'max_usuarios': 100,
            'max_hoteles': 20,
            'variantes': {
                TipoChoices.MENSUAL: 199.99,
                TipoChoices.TRIMESTRAL: 549.99,  # ~8% descuento
                TipoChoices.ANUAL: 1999.99,      # ~17% descuento
            }
        },
    ]
    
    planes_creados = 0
    planes_existentes = 0
    
    print("\n🚀 Creando planes de suscripción...\n")
    
    for plan_info in planes_data:
        nombre = plan_info['nombre']
        max_usuarios = plan_info['max_usuarios']
        max_hoteles = plan_info['max_hoteles']
        
        print(f"📦 Plan: {nombre}")
        print(f"   👥 Usuarios: {max_usuarios}")
        print(f"   🏨 Hoteles: {max_hoteles}")
        
        for tipo, precio in plan_info['variantes'].items():
            # Verificar si ya existe
            plan_existente = Plan.objects.filter(
                nombre=nombre,
                tipo=tipo
            ).first()
            
            if plan_existente:
                print(f"   ⚠️  {tipo.label}: ${precio:.2f}/mes - Ya existe (ID: {plan_existente.id})")
                planes_existentes += 1
            else:
                plan = Plan.objects.create(
                    nombre=nombre,
                    max_usuarios=max_usuarios,
                    max_hoteles=max_hoteles,
                    precio=precio,
                    tipo=tipo,
                    activo=True
                )
                print(f"   ✅ {tipo.label}: ${precio:.2f} - Creado (ID: {plan.id})")
                planes_creados += 1
        
        print()
    
    print("=" * 60)
    print(f"✅ Planes creados: {planes_creados}")
    print(f"⚠️  Planes ya existentes: {planes_existentes}")
    print(f"📊 Total de planes: {Plan.objects.count()}")
    print("=" * 60)
    
    # Mostrar resumen
    print("\n📋 Resumen de todos los planes:\n")
    for plan in Plan.objects.all().order_by('nombre', 'tipo'):
        estado = "✅ Activo" if plan.activo else "❌ Inactivo"
        print(f"  • {plan.nombre:15} | {plan.tipo:12} | ${plan.precio:8.2f} | "
              f"👥 {plan.max_usuarios:3} usuarios | 🏨 {plan.max_hoteles:2} hoteles | {estado}")
    
    print()

if __name__ == '__main__':
    crear_planes()

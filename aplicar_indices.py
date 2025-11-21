#!/usr/bin/env python
"""
Script para aplicar índices de optimización a todos los schemas de tenants

Uso:
    python aplicar_indices.py

Este script:
1. Lee el archivo indices_optimizacion.sql
2. Aplica los índices del schema public
3. Aplica los índices de tenant a TODOS los schemas de tenants
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django_tenants.utils import get_tenant_model, schema_context

def aplicar_indices_public():
    """Aplica índices en el schema public"""
    print("=" * 80)
    print("📦 APLICANDO ÍNDICES EN SCHEMA PUBLIC")
    print("=" * 80)
    
    indices_public = [
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tenant_schema_name 
        ON core_tenant(schema_name);
        """,
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_suscripcion_tenant_estado 
        ON suscripciones_suscripcion(tenant_id, estado) 
        WHERE estado IN ('activo', 'prueba');
        """
    ]
    
    with schema_context('public'):
        for idx, query in enumerate(indices_public, 1):
            try:
                print(f"\n{idx}. Ejecutando: {query.strip()[:60]}...")
                with connection.cursor() as cursor:
                    cursor.execute(query)
                print(f"   ✅ Éxito")
            except Exception as e:
                print(f"   ⚠️  Error: {e}")


def aplicar_indices_tenant(tenant):
    """Aplica índices en el schema de un tenant específico"""
    print(f"\n{'=' * 80}")
    print(f"🏨 APLICANDO ÍNDICES EN TENANT: {tenant.name} ({tenant.schema_name})")
    print(f"{'=' * 80}")
    
    indices_tenant = [
        # RESERVAS
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_reserva_estado_fecha_entrada 
        ON reservas_reserva(estado, fecha_entrada);
        """,
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_reserva_huesped_estado 
        ON reservas_reserva(huesped_id, estado);
        """,
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_reserva_habitacion 
        ON reservas_reserva(habitacion_id);
        """,
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_reserva_hotel 
        ON reservas_reserva(hotel_id);
        """,
        
        # HABITACIONES
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_habitacion_hotel_estado 
        ON habitaciones_habitacion(hotel_id, estado);
        """,
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_habitacion_tipo 
        ON habitaciones_habitacion(tipo);
        """,
        
        # FOLIOS
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_folio_huesped_estado 
        ON folioestancias_folioestancia(huesped_id, estado);
        """,
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_folio_reserva 
        ON folioestancias_folioestancia(reserva_id);
        """,
        
        # PAGOS
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pago_folio 
        ON pagos_pago(folio_estancia_id);
        """,
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pago_fecha 
        ON pagos_pago(fecha_pago DESC);
        """,
        
        # CHECK-IN/OUT
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_checkinout_reserva 
        ON checkinout_checkinout(reserva_id);
        """,
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_checkinout_fecha_checkin 
        ON checkinout_checkinout(fecha_checkin DESC);
        """,
        
        # USUARIOS
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usuario_username 
        ON usuarios_user(username);
        """,
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usuario_hotel 
        ON usuarios_user(hotel_id);
        """,
        
        # FIDELIZACIÓN
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cuenta_fidelizacion_cliente 
        ON fidelizacion_cuentafidelizacion(cliente_id);
        """,
        
        # ÍNDICES COMPUESTOS
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_reserva_huesped_fechas 
        ON reservas_reserva(huesped_id, fecha_entrada, fecha_salida);
        """,
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_habitacion_hotel_disponible 
        ON habitaciones_habitacion(hotel_id, estado) 
        WHERE estado = 'disponible';
        """
    ]
    
    with schema_context(tenant.schema_name):
        exitos = 0
        errores = 0
        
        for idx, query in enumerate(indices_tenant, 1):
            try:
                # Extraer nombre del índice para mostrar
                indice_nombre = query.split('idx_')[1].split()[0] if 'idx_' in query else 'desconocido'
                print(f"{idx:2}. Creando índice: idx_{indice_nombre}...", end=' ')
                
                with connection.cursor() as cursor:
                    cursor.execute(query)
                
                print("✅")
                exitos += 1
                
            except Exception as e:
                print(f"⚠️  {str(e)[:50]}")
                errores += 1
        
        print(f"\n📊 Resumen: {exitos} exitosos, {errores} errores")


def main():
    """Función principal"""
    print("\n" + "=" * 80)
    print("🚀 SCRIPT DE OPTIMIZACIÓN: CREACIÓN DE ÍNDICES")
    print("=" * 80)
    
    TenantModel = get_tenant_model()
    
    # 1. Aplicar índices en schema public
    aplicar_indices_public()
    
    # 2. Obtener todos los tenants (excepto public)
    tenants = TenantModel.objects.exclude(schema_name='public')
    
    print(f"\n\n📋 Se encontraron {tenants.count()} tenants para procesar")
    
    # Confirmar antes de continuar
    if tenants.count() > 0:
        respuesta = input("\n¿Desea continuar? (s/n): ")
        if respuesta.lower() != 's':
            print("❌ Operación cancelada")
            return
    
    # 3. Aplicar índices a cada tenant
    for tenant in tenants:
        try:
            aplicar_indices_tenant(tenant)
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO en tenant {tenant.schema_name}: {e}")
            continue
    
    # 4. Resumen final
    print("\n" + "=" * 80)
    print("✅ PROCESO COMPLETADO")
    print("=" * 80)
    print(f"\n📊 Índices aplicados en:")
    print(f"   - 1 schema public")
    print(f"   - {tenants.count()} schemas de tenants")
    print("\n💡 Recomendación: Ejecuta ANALYZE en PostgreSQL para actualizar estadísticas")
    print("   Comando: ANALYZE;")
    print("\n📈 Para verificar el uso de índices:")
    print("   SELECT * FROM pg_stat_user_indexes ORDER BY idx_scan DESC;")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

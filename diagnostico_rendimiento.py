#!/usr/bin/env python
"""
Script de diagnóstico de rendimiento para el sistema hotelero

Uso:
    python diagnostico_rendimiento.py

Analiza:
1. Número de queries por endpoint común
2. Tiempo de respuesta
3. Conexiones activas a BD
4. Estado del cache
5. Índices faltantes
"""

import os
import sys
import django
import time
from django.test import RequestFactory
from django.db import connection, reset_queries
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import get_tenant_model, schema_context
from apps.reservas.models import Reserva
from apps.habitaciones.models import Habitacion
from apps.usuarios.models import User
from django.core.cache import cache


def print_header(titulo):
    """Imprime un header formateado"""
    print("\n" + "=" * 80)
    print(f"📊 {titulo}")
    print("=" * 80)


def medir_queries(func, nombre_test):
    """Mide el número de queries de una función"""
    reset_queries()
    settings.DEBUG = True  # Necesario para contar queries
    
    inicio = time.time()
    resultado = func()
    fin = time.time()
    
    num_queries = len(connection.queries)
    tiempo = (fin - inicio) * 1000  # en ms
    
    print(f"\n{nombre_test}")
    print(f"  ⏱️  Tiempo: {tiempo:.2f}ms")
    print(f"  🔢 Queries: {num_queries}")
    
    if num_queries > 20:
        print(f"  ⚠️  ADVERTENCIA: Muchas queries detectadas!")
    elif num_queries > 10:
        print(f"  ⚡ Podría optimizarse más")
    else:
        print(f"  ✅ Bien optimizado")
    
    return num_queries, tiempo


def diagnosticar_tenant(tenant):
    """Diagnóstico completo de un tenant"""
    print_header(f"Tenant: {tenant.name} ({tenant.schema_name})")
    
    with schema_context(tenant.schema_name):
        
        # Test 1: Listar reservas
        def test_reservas():
            return list(Reserva.objects.all()[:10])
        
        q1, t1 = medir_queries(test_reservas, "Test 1: Listar 10 reservas")
        
        # Test 2: Reservas con select_related
        def test_reservas_optimizado():
            return list(Reserva.objects.select_related(
                'huesped', 'hotel', 'habitacion'
            ).all()[:10])
        
        q2, t2 = medir_queries(test_reservas_optimizado, "Test 2: Reservas optimizadas")
        
        # Test 3: Habitaciones
        def test_habitaciones():
            return list(Habitacion.objects.all()[:10])
        
        q3, t3 = medir_queries(test_habitaciones, "Test 3: Listar 10 habitaciones")
        
        # Test 4: Usuarios
        def test_usuarios():
            return list(User.objects.all()[:10])
        
        q4, t4 = medir_queries(test_usuarios, "Test 4: Listar 10 usuarios")
        
        # Estadísticas
        print("\n📈 Estadísticas:")
        print(f"  Total reservas: {Reserva.objects.count()}")
        print(f"  Total habitaciones: {Habitacion.objects.count()}")
        print(f"  Total usuarios: {User.objects.count()}")
        
        # Mejora por optimización
        if q1 > 0 and q2 > 0:
            mejora = ((q1 - q2) / q1) * 100
            print(f"\n💡 Mejora con select_related: {mejora:.1f}% menos queries")


def verificar_cache():
    """Verifica el funcionamiento del cache"""
    print_header("Verificación de Cache")
    
    # Test de cache
    cache_key = "test_diagnostico"
    valor_test = "valor_prueba_123"
    
    # Escribir
    cache.set(cache_key, valor_test, 60)
    print("✅ Cache WRITE: OK")
    
    # Leer
    valor_leido = cache.get(cache_key)
    if valor_leido == valor_test:
        print("✅ Cache READ: OK")
    else:
        print("❌ Cache READ: FALLO")
    
    # Limpiar
    cache.delete(cache_key)
    
    # Verificar configuración
    print(f"\n📋 Configuración de cache:")
    print(f"  Backend: {settings.CACHES['default']['BACKEND']}")
    
    if 'locmem' in settings.CACHES['default']['BACKEND']:
        print("  ⚠️  Usando cache en memoria (locmem)")
        print("  💡 Para producción, considera Redis")
    elif 'redis' in settings.CACHES['default']['BACKEND']:
        print("  ✅ Usando Redis (recomendado para producción)")


def verificar_conexion_bd():
    """Verifica la configuración de la conexión a BD"""
    print_header("Configuración de Base de Datos")
    
    db_config = settings.DATABASES['default']
    
    print(f"Engine: {db_config['ENGINE']}")
    print(f"Host: {db_config['HOST']}")
    print(f"Port: {db_config['PORT']}")
    
    # Connection pooling
    conn_max_age = db_config.get('CONN_MAX_AGE', 0)
    if conn_max_age > 0:
        print(f"✅ Connection pooling: {conn_max_age} segundos")
    else:
        print(f"⚠️  Connection pooling: DESACTIVADO (recomendado: 600)")
    
    # Opciones
    opciones = db_config.get('OPTIONS', {})
    if opciones:
        print(f"✅ Opciones configuradas: {list(opciones.keys())}")
    else:
        print(f"⚠️  Sin opciones adicionales configuradas")


def verificar_indices():
    """Verifica si existen índices importantes"""
    print_header("Verificación de Índices")
    
    indices_criticos = [
        ('core_tenant', 'idx_tenant_schema_name'),
        ('reservas_reserva', 'idx_reserva_estado_fecha_entrada'),
        ('habitaciones_habitacion', 'idx_habitacion_hotel_estado'),
    ]
    
    with connection.cursor() as cursor:
        for tabla, indice in indices_criticos:
            try:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_indexes 
                        WHERE indexname = %s
                    );
                """, [indice])
                
                existe = cursor.fetchone()[0]
                
                if existe:
                    print(f"✅ {indice}: Existe")
                else:
                    print(f"⚠️  {indice}: NO EXISTE (ejecutar aplicar_indices.py)")
                    
            except Exception as e:
                print(f"❌ Error verificando {indice}: {e}")


def main():
    """Función principal"""
    print("\n" + "=" * 80)
    print("🔍 DIAGNÓSTICO DE RENDIMIENTO DEL SISTEMA")
    print("=" * 80)
    
    # 1. Verificar cache
    verificar_cache()
    
    # 2. Verificar conexión BD
    verificar_conexion_bd()
    
    # 3. Verificar índices
    verificar_indices()
    
    # 4. Diagnóstico por tenant
    TenantModel = get_tenant_model()
    tenants = TenantModel.objects.exclude(schema_name='public')[:3]  # Solo primeros 3
    
    if tenants.exists():
        print("\n" + "=" * 80)
        print("🏨 DIAGNÓSTICO POR TENANT (Primeros 3)")
        print("=" * 80)
        
        for tenant in tenants:
            try:
                diagnosticar_tenant(tenant)
            except Exception as e:
                print(f"\n❌ Error en tenant {tenant.schema_name}: {e}")
    
    # 5. Resumen y recomendaciones
    print("\n" + "=" * 80)
    print("📋 RESUMEN Y RECOMENDACIONES")
    print("=" * 80)
    
    print("\n✅ Optimizaciones implementadas detectadas:")
    if settings.DATABASES['default'].get('CONN_MAX_AGE', 0) > 0:
        print("  - Connection pooling activado")
    
    if 'CACHES' in dir(settings) and settings.CACHES:
        print("  - Sistema de cache configurado")
    
    print("\n💡 Recomendaciones:")
    print("  1. Ejecuta 'python aplicar_indices.py' si faltan índices")
    print("  2. Monitorea el log de queries lentas en PostgreSQL")
    print("  3. Considera agregar paginación en listados grandes")
    print("  4. En producción, usa Redis en lugar de locmem cache")
    
    print("\n📊 Para más detalles, activa Django Debug Toolbar en desarrollo")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

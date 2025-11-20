"""
Script para consolidar (squash) migraciones de todas las apps
Esto reduce drásticamente el tiempo de creación de nuevos tenants

Uso:
    python squash_all_migrations.py

ADVERTENCIA: 
- Hacer backup de la base de datos antes de ejecutar
- Probar en entorno de desarrollo primero
- Hacer commit de cambios antes de ejecutar
"""

import subprocess
import sys
from pathlib import Path

# Apps que tienen migraciones y queremos consolidar
APPS_TO_SQUASH = [
    ('usuarios', '0001', '0005'),  # usuarios tiene 5 migraciones
    ('habitaciones', '0001', '0002'),
    ('servicios', '0001', '0002'),
    ('pagos', '0001', '0004'),
    ('servicios_asociados', '0001', '0006'),
    ('suscripciones', '0001', '0005'),
    ('auditlog', '0001', '0017'),  # Muchas migraciones de auditlog
    ('token_blacklist', '0001', '0013'),  # Muchas migraciones de JWT
]

def run_command(command):
    """Ejecuta un comando y muestra output"""
    print(f"\n🔹 Ejecutando: {command}")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("⚠️ Warnings:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def squash_migrations():
    """Consolida las migraciones de todas las apps"""
    
    print("=" * 60)
    print("🚀 CONSOLIDACIÓN DE MIGRACIONES")
    print("=" * 60)
    print("\nEste proceso consolidará las migraciones de las siguientes apps:")
    for app, start, end in APPS_TO_SQUASH:
        print(f"  - {app}: desde {start} hasta {end}")
    
    response = input("\n¿Continuar? (s/n): ")
    if response.lower() != 's':
        print("❌ Operación cancelada")
        return
    
    success_count = 0
    failed_apps = []
    
    for app, start_migration, end_migration in APPS_TO_SQUASH:
        print(f"\n{'=' * 60}")
        print(f"📦 Procesando app: {app}")
        print(f"{'=' * 60}")
        
        # Verificar que la app existe
        app_path = Path(f"apps/{app}")
        if not app_path.exists():
            print(f"⚠️ App {app} no encontrada en apps/. Saltando...")
            continue
        
        # Construir comando de squash
        command = f"python manage.py squashmigrations apps.{app} {start_migration} {end_migration} --noinput"
        
        if run_command(command):
            print(f"✅ {app}: Migraciones consolidadas exitosamente")
            success_count += 1
        else:
            print(f"❌ {app}: Error al consolidar migraciones")
            failed_apps.append(app)
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print(f"✅ Apps procesadas exitosamente: {success_count}/{len(APPS_TO_SQUASH)}")
    
    if failed_apps:
        print(f"❌ Apps con errores: {', '.join(failed_apps)}")
    
    print("\n" + "=" * 60)
    print("📝 PRÓXIMOS PASOS")
    print("=" * 60)
    print("""
1. Revisar los archivos de migración generados en cada app
2. Eliminar las migraciones antiguas si la consolidación fue exitosa
3. Probar las migraciones consolidadas:
   python manage.py migrate --fake-initial
4. Hacer commit de los cambios:
   git add .
   git commit -m "perf: Consolidar migraciones para optimizar creación de tenants"
5. Deploy a producción

⚠️ IMPORTANTE: Las instancias que ya tienen las migraciones aplicadas
   necesitarán usar --fake para marcar las squashed migrations como aplicadas:
   python manage.py migrate --fake
""")

def show_migration_stats():
    """Muestra estadísticas de migraciones actuales"""
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS DE MIGRACIONES ACTUALES")
    print("=" * 60)
    
    command = "python manage.py showmigrations"
    run_command(command)

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║  🚀 Script de Consolidación de Migraciones                ║
║                                                           ║
║  Este script consolidará las migraciones para reducir    ║
║  el tiempo de creación de tenants de 5-6 min a 1-2 min  ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # Verificar que estamos en el directorio correcto
    if not Path("manage.py").exists():
        print("❌ Error: Este script debe ejecutarse desde el directorio raíz del proyecto")
        print("   (donde está manage.py)")
        sys.exit(1)
    
    # Mostrar estadísticas actuales
    show_migration_stats()
    
    # Ejecutar consolidación
    squash_migrations()

"""
Comando para limpiar backups antiguos según la política de retención
"""
from django.core.management.base import BaseCommand
from apps.backups.utils import (
    create_backup_directory,
    cleanup_old_backups,
    get_backup_config,
    get_backup_stats,
    eliminar_backup_de_s3
)


class Command(BaseCommand):
    help = 'Elimina backups antiguos según la política de retención configurada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='all',
            choices=['all', 'full', 'tenant'],
            help='Tipo de backups a limpiar'
        )
        parser.add_argument(
            '--older-than',
            type=int,
            default=None,
            help='Eliminar backups más antiguos de N días'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular sin eliminar archivos'
        )

    def handle(self, *args, **options):
        backup_type = options['type']
        older_than = options['older_than']
        dry_run = options['dry_run']
        
        # Obtener configuración
        config = get_backup_config()
        retention_days = older_than if older_than else config['retention_days']
        
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('🧹 LIMPIEZA DE BACKUPS ANTIGUOS'))
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(f'\n📅 Retención: {retention_days} días')
        self.stdout.write(f'🔍 Tipo: {backup_type}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  MODO SIMULACIÓN (no se eliminará nada)\n'))
        
        total_deleted = 0
        total_freed = 0
        
        # Determinar qué carpetas limpiar
        dirs_to_clean = []
        if backup_type in ['all', 'full']:
            dirs_to_clean.append(('full', create_backup_directory('full')))
        if backup_type in ['all', 'tenant']:
            dirs_to_clean.append(('tenant', create_backup_directory('tenant')))
        
        # Limpiar cada carpeta
        for dir_name, dir_path in dirs_to_clean:
            self.stdout.write(f'\n📂 Procesando carpeta: {dir_name}/')
            
            # Obtener estadísticas antes
            stats_before = get_backup_stats(dir_path)
            self.stdout.write(f'   Archivos actuales: {stats_before["total_backups"]}')
            self.stdout.write(f'   Espacio usado: {stats_before["total_size_mb"]:.2f} MB')
            
            if not dry_run:
                # Eliminar de S3 (donde se guardan los backups ahora)
                from apps.backups.models import Backup
                from django.conf import settings
                from datetime import datetime, timedelta
                
                if getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None):
                    self.stdout.write('   ☁️  Eliminando backups antiguos de S3...')
                    
                    cutoff_date = datetime.now() - timedelta(days=retention_days)
                    backups_s3 = Backup.objects.filter(
                        archivo__startswith='https://'
                    )
                    
                    deleted_s3 = 0
                    for backup in backups_s3:
                        # Verificar si es antiguo
                        if backup.fecha.replace(tzinfo=None) < cutoff_date:
                            if eliminar_backup_de_s3(backup.archivo):
                                backup.delete()
                                deleted_s3 += 1
                                self.stdout.write(self.style.SUCCESS(f'   ✅ Eliminado de S3: {backup.archivo.split("/")[-1]}'))
                    
                    if deleted_s3 > 0:
                        self.stdout.write(self.style.SUCCESS(f'   ✅ Eliminados de S3: {deleted_s3} archivos'))
                    else:
                        self.stdout.write(self.style.SUCCESS('   ℹ️  No hay backups antiguos en S3'))
                
                total_deleted += deleted_s3
                
                if deleted > 0:
                    self.stdout.write(self.style.SUCCESS(f'   ✅ Eliminados: {deleted} archivos'))
                    self.stdout.write(self.style.SUCCESS(f'   💾 Espacio liberado: {freed / 1024 / 1024:.2f} MB'))
                else:
                    self.stdout.write(self.style.SUCCESS('   ℹ️  No hay archivos antiguos para eliminar'))
            else:
                # Contar cuántos se eliminarían (simulación)
                from datetime import datetime, timedelta
                cutoff_date = datetime.now() - timedelta(days=retention_days)
                would_delete = sum(
                    1 for f in dir_path.glob('*.sql')
                    if datetime.fromtimestamp(f.stat().st_mtime) < cutoff_date
                )
                would_free = sum(
                    f.stat().st_size for f in dir_path.glob('*.sql')
                    if datetime.fromtimestamp(f.stat().st_mtime) < cutoff_date
                )
                
                self.stdout.write(self.style.WARNING(f'   🔮 Se eliminarían: {would_delete} archivos'))
                self.stdout.write(self.style.WARNING(f'   🔮 Se liberarían: {would_free / 1024 / 1024:.2f} MB'))
        
        # Resumen final
        self.stdout.write(self.style.WARNING('\n' + '=' * 60))
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'📊 Total eliminado: {total_deleted} archivos'))
            self.stdout.write(self.style.SUCCESS(f'💾 Total liberado: {total_freed / 1024 / 1024:.2f} MB'))
        else:
            self.stdout.write(self.style.WARNING('ℹ️  SIMULACIÓN COMPLETADA - No se eliminó nada'))
        self.stdout.write(self.style.WARNING('=' * 60 + '\n'))

"""
Comando para crear backups individuales de cada tenant (schema)
"""
import time
from datetime import datetime
from django.core.management.base import BaseCommand
from django_tenants.utils import get_tenant_model
from apps.backups.models import Backup
from apps.backups.utils import (
    create_backup_directory,
    generate_backup_filename,
    execute_pg_dump,
    subir_backup_a_s3
)


class Command(BaseCommand):
    help = 'Genera backups individuales de todos los tenants (schemas)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            default=None,
            help='Nombre del schema específico a respaldar (opcional)'
        )
        parser.add_argument(
            '--type',
            type=str,
            default='manual',
            choices=['manual', 'auto_daily', 'auto_weekly', 'auto_monthly'],
            help='Tipo de backup'
        )

    def handle(self, *args, **options):
        schema_filter = options['schema']
        tipo = options['type']
        
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('🏨 BACKUP DE TENANTS INDIVIDUALES'))
        self.stdout.write(self.style.WARNING('=' * 60))
        
        # Obtener tenants
        tenants = get_tenant_model().objects.exclude(schema_name='public')
        
        if schema_filter:
            tenants = tenants.filter(schema_name=schema_filter)
            if not tenants.exists():
                self.stdout.write(self.style.ERROR(f'\n❌ Tenant "{schema_filter}" no encontrado\n'))
                return
        
        total_tenants = tenants.count()
        self.stdout.write(f'\n📊 Tenants a respaldar: {total_tenants}\n')
        
        # Crear carpeta de backups
        backup_dir = create_backup_directory('tenant')
        
        successful = 0
        failed = 0
        
        for tenant in tenants:
            self.stdout.write(f'\n🔹 Procesando: {tenant.schema_name}')
            
            # Generar nombre de archivo
            filename = generate_backup_filename('tenant', tenant.schema_name)
            output_file = backup_dir / filename
            
            # Crear registro en la base de datos
            backup_record = Backup.objects.create(
                tenant=tenant,
                archivo=f'backups/tenant/{filename}',
                tipo=tipo,
                backup_type='tenant',
                estado='en_progreso',
                mensaje='Backup en progreso...'
            )
            
            # Ejecutar pg_dump
            start_time = time.time()
            success, message = execute_pg_dump(output_file, schema_name=tenant.schema_name)
            duration = int(time.time() - start_time)
            
            # Actualizar registro
            if success:
                file_size = output_file.stat().st_size
                backup_record.estado = 'ok'
                backup_record.mensaje = message
                backup_record.tamaño_bytes = file_size
                backup_record.duracion_segundos = duration
                
                # Subir a S3 (obligatorio)
                from django.conf import settings
                bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
                if bucket_name:
                    self.stdout.write('   ☁️  Subiendo a S3...')
                    s3_url = subir_backup_a_s3(str(output_file), tenant_name=tenant.schema_name)
                    if s3_url:
                        backup_record.archivo = s3_url  # Guardar URL de S3
                        self.stdout.write(self.style.SUCCESS('   ✅ Subido a S3'))
                        
                        # Eliminar archivo local después de subir a S3
                        if output_file.exists():
                            output_file.unlink()
                            self.stdout.write(self.style.SUCCESS('   🗑️  Archivo local eliminado'))
                    else:
                        self.stdout.write(self.style.ERROR('   ❌ No se pudo subir a S3'))
                        backup_record.estado = 'error'
                        backup_record.mensaje = 'Error al subir a S3'
                else:
                    self.stdout.write(self.style.ERROR('   ❌ AWS_STORAGE_BUCKET_NAME no configurado'))
                    backup_record.estado = 'error'
                    backup_record.mensaje = 'AWS_STORAGE_BUCKET_NAME no configurado'
                
                backup_record.save()
                
                if backup_record.estado == 'ok':
                    successful += 1
                    self.stdout.write(self.style.SUCCESS(f'   ✅ {message}'))
                    self.stdout.write(self.style.SUCCESS(f'   ⏱️  Duración: {duration}s'))
                else:
                    failed += 1
            else:
                backup_record.estado = 'error'
                backup_record.mensaje = message
                backup_record.duracion_segundos = duration
                backup_record.save()
                
                failed += 1
                self.stdout.write(self.style.ERROR(f'   ❌ {message}'))
                
                # Eliminar archivo si hay error
                if output_file.exists():
                    output_file.unlink()
        
        # Resumen final
        self.stdout.write(self.style.WARNING('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS(f'✅ Exitosos: {successful}'))
        if failed > 0:
            self.stdout.write(self.style.ERROR(f'❌ Fallidos: {failed}'))
        self.stdout.write(self.style.SUCCESS(f'📁 Carpeta: {backup_dir}'))
        self.stdout.write(self.style.WARNING('=' * 60 + '\n'))


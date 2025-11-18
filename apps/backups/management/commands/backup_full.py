"""
Comando para crear backup completo de toda la base de datos
Incluye el schema public y todos los schemas de tenants
"""
import time
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import connection
from apps.backups.models import Backup
from apps.backups.utils import (
    create_backup_directory,
    generate_backup_filename,
    execute_pg_dump,
    get_backup_config
)


class Command(BaseCommand):
    help = 'Crea un backup completo de toda la base de datos (todos los schemas)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='manual',
            choices=['manual', 'auto_daily', 'auto_weekly', 'auto_monthly'],
            help='Tipo de backup'
        )

    def handle(self, *args, **options):
        tipo = options['type']
        
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('🗄️  BACKUP COMPLETO DE BASE DE DATOS'))
        self.stdout.write(self.style.WARNING('=' * 60))
        
        # Crear carpeta de backups
        backup_dir = create_backup_directory('full')
        filename = generate_backup_filename('full')
        output_file = backup_dir / filename
        
        self.stdout.write(f'\n📁 Carpeta: {backup_dir}')
        self.stdout.write(f'📄 Archivo: {filename}')
        self.stdout.write(f'🕐 Iniciado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        
        # Forzar uso del schema public para guardar el registro
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO public;")
        
        # Crear registro en la base de datos
        backup_record = Backup.objects.using('default').create(
            tenant=None,  # Backup completo no tiene tenant específico
            archivo=f'backups/full/{filename}',
            tipo=tipo,
            backup_type='full',
            estado='en_progreso',
            mensaje='Backup en progreso...'
        )
        
        # Ejecutar pg_dump
        start_time = time.time()
        success, message = execute_pg_dump(output_file, schema_name=None)
        duration = int(time.time() - start_time)
        
        # Actualizar registro
        if success:
            file_size = output_file.stat().st_size
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO public;")
            backup_record.estado = 'ok'
            backup_record.mensaje = message
            backup_record.tamaño_bytes = file_size
            backup_record.duracion_segundos = duration
            backup_record.save(using='default')
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ {message}'))
            self.stdout.write(self.style.SUCCESS(f'⏱️  Duración: {duration} segundos'))
            self.stdout.write(self.style.SUCCESS(f'📦 Archivo: {output_file}'))
            self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        else:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO public;")
            backup_record.estado = 'error'
            backup_record.mensaje = message
            backup_record.duracion_segundos = duration
            backup_record.save(using='default')
            
            self.stdout.write(self.style.ERROR(f'\n❌ {message}'))
            self.stdout.write(self.style.ERROR('\n' + '=' * 60))
            
            # Eliminar archivo si hay error
            if output_file.exists():
                output_file.unlink()

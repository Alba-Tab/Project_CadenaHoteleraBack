"""
ViewSet para gestionar backups desde la API REST
"""
import time
from pathlib import Path
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.http import FileResponse
from django_tenants.utils import get_tenant_model
from .models import Backup
from .serializers import BackupSerializer, BackupStatsSerializer
from .utils import (
    create_backup_directory,
    generate_backup_filename,
    execute_pg_dump,
    execute_pg_restore,
    get_backup_stats,
    get_backup_config
)


class BackupViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar backups
    """
    queryset = Backup.objects.all().order_by('-fecha')
    serializer_class = BackupSerializer
    permission_classes = [IsAdminUser]  # Solo administradores
    
    def get_queryset(self):
        """
        Filtrar backups por parámetros de query
        """
        queryset = super().get_queryset()
        
        # Filtrar por tipo
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por tenant
        tenant_schema = self.request.query_params.get('tenant', None)
        if tenant_schema:
            queryset = queryset.filter(tenant__schema_name=tenant_schema)
        
        # Filtrar por tipo de backup
        backup_type = self.request.query_params.get('backup_type', None)
        if backup_type:
            queryset = queryset.filter(backup_type=backup_type)
        
        return queryset
    
    @action(detail=False, methods=['post'], url_path='crear-full')
    def crear_backup_full(self, request):
        """
        POST /api/backups/crear-full/
        Crea un backup completo de toda la base de datos
        """
        tipo = request.data.get('tipo', 'manual')
        
        # Crear carpeta y archivo
        backup_dir = create_backup_directory('full')
        filename = generate_backup_filename('full')
        output_file = backup_dir / filename
        
        # Crear registro
        backup_record = Backup.objects.create(
            tenant=None,
            archivo=f'backups/full/{filename}',
            tipo=tipo,
            backup_type='full',
            estado='en_progreso',
            mensaje='Backup en progreso...'
        )
        
        # Ejecutar backup
        start_time = time.time()
        success, message = execute_pg_dump(output_file, schema_name=None)
        duration = int(time.time() - start_time)
        
        # Actualizar registro
        if success:
            file_size = output_file.stat().st_size
            backup_record.estado = 'ok'
            backup_record.mensaje = message
            backup_record.tamaño_bytes = file_size
            backup_record.duracion_segundos = duration
            backup_record.save()
            
            serializer = self.get_serializer(backup_record)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            backup_record.estado = 'error'
            backup_record.mensaje = message
            backup_record.duracion_segundos = duration
            backup_record.save()
            
            if output_file.exists():
                output_file.unlink()
            
            return Response(
                {'error': message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='crear-tenants')
    def crear_backup_tenants(self, request):
        """
        POST /api/backups/crear-tenants/
        Crea backups de todos los tenants
        """
        tipo = request.data.get('tipo', 'manual')
        schema_filter = request.data.get('schema', None)
        
        # Obtener tenants
        tenants = get_tenant_model().objects.exclude(schema_name='public')
        if schema_filter:
            tenants = tenants.filter(schema_name=schema_filter)
        
        if not tenants.exists():
            return Response(
                {'error': 'No se encontraron tenants'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        backup_dir = create_backup_directory('tenant')
        resultados = []
        
        for tenant in tenants:
            filename = generate_backup_filename('tenant', tenant.schema_name)
            output_file = backup_dir / filename
            
            backup_record = Backup.objects.create(
                tenant=tenant,
                archivo=f'backups/tenant/{filename}',
                tipo=tipo,
                backup_type='tenant',
                estado='en_progreso'
            )
            
            start_time = time.time()
            success, message = execute_pg_dump(output_file, schema_name=tenant.schema_name)
            duration = int(time.time() - start_time)
            
            if success:
                file_size = output_file.stat().st_size
                backup_record.estado = 'ok'
                backup_record.mensaje = message
                backup_record.tamaño_bytes = file_size
                backup_record.duracion_segundos = duration
                backup_record.save()
            else:
                backup_record.estado = 'error'
                backup_record.mensaje = message
                backup_record.duracion_segundos = duration
                backup_record.save()
                
                if output_file.exists():
                    output_file.unlink()
            
            resultados.append({
                'tenant': tenant.schema_name,
                'estado': backup_record.estado,
                'mensaje': message,
                'archivo': filename
            })
        
        return Response({'resultados': resultados}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], url_path='descargar')
    def descargar_backup(self, request, pk=None):
        """
        GET /api/backups/{id}/descargar/
        Descarga un archivo de backup
        """
        backup = self.get_object()
        file_path = Path(backup.archivo.path)
        
        if not file_path.exists():
            return Response(
                {'error': 'Archivo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=file_path.name
        )
    
    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        """
        GET /api/backups/estadisticas/
        Retorna estadísticas de los backups
        """
        backup_full_dir = create_backup_directory('full')
        backup_tenant_dir = create_backup_directory('tenant')
        
        stats_full = get_backup_stats(backup_full_dir)
        stats_tenant = get_backup_stats(backup_tenant_dir)
        
        # Estadísticas desde la BD
        total_backups_db = Backup.objects.count()
        exitosos_db = Backup.objects.filter(estado='ok').count()
        fallidos_db = Backup.objects.filter(estado='error').count()
        
        stats_full['exitosos'] = exitosos_db
        stats_full['fallidos'] = fallidos_db
        
        return Response({
            'full': stats_full,
            'tenant': stats_tenant,
            'base_datos': {
                'total': total_backups_db,
                'exitosos': exitosos_db,
                'fallidos': fallidos_db,
            }
        })
    
    @action(detail=False, methods=['get'], url_path='configuracion')
    def configuracion(self, request):
        """
        GET /api/backups/configuracion/
        Retorna la configuración actual de backups
        """
        config = get_backup_config()
        return Response(config)


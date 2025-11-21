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
from django_tenants.utils import get_tenant_model, schema_context
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
        Siempre lee desde el schema público
        """
        # Usar schema_context para asegurar que leemos del schema público
        with schema_context('public'):
            queryset = Backup.objects.all().order_by('-fecha')
            
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
            
            # Convertir a lista para poder usar fuera del context
            return list(queryset)
    
    def get_object(self):
        """
        Obtener un backup específico desde el schema público
        NO USAR - causa problemas con lazy evaluation
        """
        pk = self.kwargs.get('pk')
        with schema_context('public'):
            try:
                backup = Backup.objects.get(pk=pk)
                # Forzar evaluación de campos relacionados
                if backup.tenant:
                    _ = backup.tenant.schema_name
                return backup
            except Backup.DoesNotExist:
                return None
    
    def destroy(self, request, pk=None):
        """
        DELETE /api/backups/{id}/
        Elimina un backup (archivo y registro)
        """
        try:
            with schema_context('public'):
                backup = Backup.objects.get(pk=pk)
                
                # Eliminar archivo físico
                try:
                    file_path = Path(backup.archivo.path)
                    if file_path.exists():
                        file_path.unlink()
                except Exception:
                    pass
                
                # Eliminar registro
                backup.delete()
            
            return Response(
                {'mensaje': 'Backup eliminado correctamente'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Backup.DoesNotExist:
            return Response(
                {'error': 'Backup no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
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
        
        # Crear registro en el schema público usando schema_context
        with schema_context('public'):
            backup_record = Backup.objects.create(
                tenant=None,
                archivo=f'backups/full/{filename}',
                tipo=tipo,
                backup_type='full',
                estado='en_progreso',
                mensaje='Backup en progreso...'
            )
            backup_id = backup_record.id
        
        # Ejecutar backup
        start_time = time.time()
        success, message = execute_pg_dump(output_file, schema_name=None)
        duration = int(time.time() - start_time)
        
        # Actualizar registro en el schema público
        with schema_context('public'):
            backup_record = Backup.objects.get(id=backup_id)
            if success:
                file_size = output_file.stat().st_size
                backup_record.estado = 'ok'
                backup_record.mensaje = message
                backup_record.tamaño_bytes = file_size
                backup_record.duracion_segundos = duration
                
                # Subir a S3 (obligatorio)
                from django.conf import settings
                from .utils import subir_backup_a_s3
                
                bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
                if bucket_name:
                    s3_url = subir_backup_a_s3(str(output_file), tenant_name='full')
                    if s3_url:
                        backup_record.archivo = s3_url  # Guardar URL de S3
                        
                        # Eliminar archivo local después de subir a S3
                        if output_file.exists():
                            output_file.unlink()
                    else:
                        backup_record.estado = 'error'
                        backup_record.mensaje = 'Error al subir a S3'
                else:
                    backup_record.estado = 'error'
                    backup_record.mensaje = 'AWS_STORAGE_BUCKET_NAME no configurado'
                
                backup_record.save()
                
                if backup_record.estado == 'ok':
                    serializer = self.get_serializer(backup_record)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        {'error': backup_record.mensaje},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
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
        
        # Obtener tenants (estos están en el schema público)
        with schema_context('public'):
            tenants = get_tenant_model().objects.exclude(schema_name='public')
            if schema_filter:
                tenants = tenants.filter(schema_name=schema_filter)
            
            if not tenants.exists():
                return Response(
                    {'error': 'No se encontraron tenants'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Convertir a lista para usar fuera del context
            tenants_list = list(tenants)
        
        backup_dir = create_backup_directory('tenant')
        resultados = []
        
        for tenant in tenants_list:
            filename = generate_backup_filename('tenant', tenant.schema_name)
            output_file = backup_dir / filename
            
            # Crear registro en schema público
            with schema_context('public'):
                backup_record = Backup.objects.create(
                    tenant=tenant,
                    archivo=f'backups/tenant/{filename}',
                    tipo=tipo,
                    backup_type='tenant',
                    estado='en_progreso'
                )
                backup_id = backup_record.id
            
            start_time = time.time()
            success, message = execute_pg_dump(output_file, schema_name=tenant.schema_name)
            duration = int(time.time() - start_time)
            
            # Actualizar registro en schema público
            with schema_context('public'):
                backup_record = Backup.objects.get(id=backup_id)
                if success:
                    file_size = output_file.stat().st_size
                    backup_record.estado = 'ok'
                    backup_record.mensaje = message
                    backup_record.tamaño_bytes = file_size
                    backup_record.duracion_segundos = duration
                    
                    # Subir a S3 (obligatorio)
                    from django.conf import settings
                    from .utils import subir_backup_a_s3
                    
                    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
                    if bucket_name:
                        s3_url = subir_backup_a_s3(str(output_file), tenant_name=tenant.schema_name)
                        if s3_url:
                            backup_record.archivo = s3_url  # Guardar URL de S3
                            
                            # Eliminar archivo local después de subir a S3
                            if output_file.exists():
                                output_file.unlink()
                        else:
                            backup_record.estado = 'error'
                            backup_record.mensaje = 'Error al subir a S3'
                    else:
                        backup_record.estado = 'error'
                        backup_record.mensaje = 'AWS_STORAGE_BUCKET_NAME no configurado'
                    
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
        Descarga un archivo de backup o genera URL firmada si está en S3
        """
        from django.conf import settings
        from .utils import generar_url_firmada_s3
        
        # Obtener backup desde schema público
        with schema_context('public'):
            try:
                backup = Backup.objects.get(pk=pk)
                archivo_url = str(backup.archivo)
            except Backup.DoesNotExist:
                return Response(
                    {'error': 'Backup no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Verificar si el archivo está en S3
        is_s3_file = archivo_url.startswith('https://') or archivo_url.startswith('s3://')
        
        if is_s3_file:
            # Generar URL firmada para descarga temporal (válida por 1 hora)
            url_firmada = generar_url_firmada_s3(archivo_url, expiracion_segundos=3600)
            
            if url_firmada:
                return Response({
                    'url': url_firmada,
                    'expira_en_segundos': 3600,
                    'mensaje': 'URL de descarga temporal generada (válida por 1 hora)'
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Error al generar URL de descarga'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            # Archivo local - descarga directa
            media_root = getattr(settings, 'MEDIA_ROOT', Path(settings.BASE_DIR) / 'media')
            file_path = Path(media_root) / archivo_url
            
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
    
    @action(detail=True, methods=['post'], url_path='restaurar')
    def restaurar_backup(self, request, pk=None):
        """
        POST /api/backups/{id}/restaurar/
        Restaura un backup (completo o de un tenant específico) desde S3
        """
        from django.conf import settings
        import tempfile
        import boto3
        from botocore.exceptions import ClientError
        
        # Obtener información del backup desde schema público
        with schema_context('public'):
            try:
                backup = Backup.objects.get(pk=pk)
                backup_id = backup.id
                backup_estado = backup.estado
                backup_type = backup.backup_type
                archivo_url = str(backup.archivo)
                
                # Obtener schema_name si es un tenant
                schema_name = None
                if backup.backup_type == 'tenant' and backup.tenant:
                    schema_name = backup.tenant.schema_name
                    
            except Backup.DoesNotExist:
                return Response(
                    {'error': 'Backup no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Verificar que el backup está en estado OK
        if backup_estado != 'ok':
            return Response(
                {'error': 'No se puede restaurar un backup con errores'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determinar si el archivo está en S3 o local
        is_s3_file = archivo_url.startswith('https://') or archivo_url.startswith('s3://')
        
        if is_s3_file:
            # CASO 1: Archivo en S3 - Descargar temporalmente
            try:
                # Configurar cliente S3
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )
                
                bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                
                # Extraer key del URL
                s3_key = archivo_url.split('.amazonaws.com/')[-1]
                
                # Crear archivo temporal (cerrar el handle antes de usarlo)
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.sql')
                temp_path = Path(tmp_file.name)
                tmp_file.close()  # ✅ Cerrar el archivo ANTES de descargar
                
                try:
                    # Descargar de S3
                    s3_client.download_file(bucket_name, s3_key, str(temp_path))
                    
                    # Ejecutar restauración
                    start_time = time.time()
                    success, message = execute_pg_restore(temp_path, schema_name=schema_name)
                    duration = int(time.time() - start_time)
                    
                    if success:
                        return Response({
                            'mensaje': message,
                            'backup_id': backup_id,
                            'tipo': backup_type,
                            'tenant': schema_name if schema_name else 'Completo',
                            'duracion_segundos': duration,
                            'origen': 's3'
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response(
                            {'error': message},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                finally:
                    # Eliminar archivo temporal siempre
                    if temp_path.exists():
                        temp_path.unlink()
                        
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                error_message = e.response.get('Error', {}).get('Message', str(e))
                return Response(
                    {'error': f'Error al descargar de S3 [{error_code}]: {error_message}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as e:
                return Response(
                    {'error': f'Error inesperado: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            # CASO 2: Archivo local (para backups antiguos)
            media_root = getattr(settings, 'MEDIA_ROOT', Path(settings.BASE_DIR) / 'media')
            file_path = Path(media_root) / archivo_url
            
            if not file_path.exists():
                return Response(
                    {
                        'error': 'Archivo de backup no encontrado',
                        'ruta_buscada': str(file_path),
                        'archivo_db': archivo_url
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Ejecutar restauración
            start_time = time.time()
            success, message = execute_pg_restore(file_path, schema_name=schema_name)
            duration = int(time.time() - start_time)
            
            if success:
                return Response({
                    'mensaje': message,
                    'backup_id': backup_id,
                    'tipo': backup_type,
                    'tenant': schema_name if schema_name else 'Completo',
                    'duracion_segundos': duration,
                    'origen': 'local'
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': message},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
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


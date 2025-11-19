from rest_framework import serializers
from .models import Backup


class BackupSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Backup con información adicional
    """
    tenant_nombre = serializers.CharField(source='tenant.name', read_only=True, allow_null=True)
    tenant_schema = serializers.CharField(source='tenant.schema_name', read_only=True, allow_null=True)
    tamaño_mb = serializers.FloatField(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    backup_type_display = serializers.CharField(source='get_backup_type_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    es_exitoso = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Backup
        fields = [
            'id',
            'tenant',
            'tenant_nombre',
            'tenant_schema',
            'archivo',
            'tipo',
            'tipo_display',
            'backup_type',
            'backup_type_display',
            'fecha',
            'estado',
            'estado_display',
            'mensaje',
            'tamaño_bytes',
            'tamaño_mb',
            'duracion_segundos',
            'es_exitoso',
        ]
        read_only_fields = [
            'id',
            'fecha',
            'estado',
            'mensaje',
            'tamaño_bytes',
            'duracion_segundos',
        ]


class BackupStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de backups
    """
    total_backups = serializers.IntegerField()
    total_size = serializers.IntegerField()
    total_size_mb = serializers.FloatField()
    oldest = serializers.DateTimeField(allow_null=True)
    newest = serializers.DateTimeField(allow_null=True)
    exitosos = serializers.IntegerField(required=False)
    fallidos = serializers.IntegerField(required=False)


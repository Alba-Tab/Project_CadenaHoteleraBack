from django.db import models
from django.conf import settings


class Backup(models.Model):
    """
    Modelo para registrar el historial de backups realizados
    """
    TIPO_CHOICES = (
        ('manual', 'Manual'),
        ('auto_daily', 'Automático Diario'),
        ('auto_weekly', 'Automático Semanal'),
        ('auto_monthly', 'Automático Mensual'),
    )
    
    BACKUP_TYPE_CHOICES = (
        ('full', 'Completo'),
        ('tenant', 'Por Tenant'),
    )
    
    ESTADO_CHOICES = (
        ('ok', 'Correcto'),
        ('error', 'Fallido'),
        ('en_progreso', 'En Progreso'),
    )
    
    tenant = models.ForeignKey(
        settings.TENANT_MODEL,  # Usar string reference en lugar de get_tenant_model()
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Tenant asociado (null para backups completos)'
    )
    archivo = models.FileField(upload_to='backups/', max_length=500)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='manual')
    backup_type = models.CharField(
        max_length=20, 
        choices=BACKUP_TYPE_CHOICES, 
        default='tenant',
        help_text='Tipo de backup realizado'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='en_progreso')
    mensaje = models.TextField(blank=True, null=True)
    tamaño_bytes = models.BigIntegerField(default=0, help_text='Tamaño del archivo en bytes')
    duracion_segundos = models.IntegerField(default=0, help_text='Duración del backup en segundos')
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Backup'
        verbose_name_plural = 'Backups'
    
    def __str__(self):
        if self.tenant:
            return f"{self.tenant.schema_name} ({self.get_tipo_display()}) - {self.fecha.strftime('%Y-%m-%d %H:%M')}"
        return f"Backup Completo ({self.get_tipo_display()}) - {self.fecha.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def tamaño_mb(self):
        """Retorna el tamaño en megabytes"""
        return round(self.tamaño_bytes / 1024 / 1024, 2)
    
    @property
    def es_exitoso(self):
        """Indica si el backup fue exitoso"""
        return self.estado == 'ok'


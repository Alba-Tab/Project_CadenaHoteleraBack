from django.db import models
from apps.habitaciones.models import Hotel

# Tu modelo ConfiguracionApariencia actual debe estar así:
class ConfiguracionApariencia(models.Model):
    # Relación con Hotel (como ya lo tienes)
    hotel = models.OneToOneField(
        Hotel,
        on_delete=models.CASCADE,
        related_name='configuracion_apariencia',
        verbose_name='Hotel'
    )

    # Los campos de personalización (como los definimos antes)
    color_primario = models.CharField(max_length=7, default='#00a1ff')
    color_secundario = models.CharField(max_length=7, default='#16cdc7')
    color_fondo = models.CharField(max_length=7, default='#f8fafd')
    familia_fuente = models.CharField(max_length=50, default='Inter')
    tamano_fuente_base = models.PositiveIntegerField(default=14)
    modo_tema = models.CharField(
        max_length=6,
        choices=[('claro', 'Claro'), ('oscuro', 'Oscuro')],
        default='claro'
    )

    # Campos adicionales que podrías tener
    logo_key = models.CharField(max_length=100, blank=True, null=True)
    tema = models.CharField(max_length=50, default='Por defecto')
    tipo_letra = models.CharField(max_length=50, default='Inter')

    # Fechas
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración de Apariencia'
        verbose_name_plural = 'Configuraciones de Apariencia'
        db_table = 'configuracion_apariencia'

    def __str__(self):
        return f'Configuración de {self.hotel.nombre}'

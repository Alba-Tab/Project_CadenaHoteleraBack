from django.db import models
from apps.habitaciones.models import Habitacion
from apps.usuarios.models import User


class RecomendacionPrecio(models.Model):
    """
    Modelo para almacenar recomendaciones de precios generadas por IA
    Temporal: se guardan antes de ser aceptadas por el administrador
    """
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.CASCADE,
        related_name='recomendaciones'
    )
    tarifa_actual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Precio actual de la habitación'
    )
    tarifa_sugerida = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Precio sugerido por el modelo de IA'
    )
    confianza = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Porcentaje de confianza del modelo (0-100)'
    )
    motivo = models.TextField(
        help_text='Explicación de por qué se sugiere este precio'
    )
    fecha_generacion = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha y hora de generación de la recomendación'
    )
    aceptada = models.BooleanField(
        default=False,
        help_text='Indica si la recomendación fue aceptada'
    )
    aplicada = models.BooleanField(
        default=False,
        help_text='Indica si el precio ya fue aplicado a la habitación'
    )
    
    class Meta:
        verbose_name = 'Recomendación de Precio'
        verbose_name_plural = 'Recomendaciones de Precios'
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f'{self.habitacion} - {self.tarifa_sugerida} Bs ({self.confianza}%)'


class HistorialRecomendacion(models.Model):
    """
    Modelo para registrar el historial de recomendaciones aceptadas
    Permanente: auditoría de cambios de precios
    """
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.CASCADE,
        related_name='historial_precios'
    )
    tarifa_anterior = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Precio antes del cambio'
    )
    tarifa_nueva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Precio después del cambio'
    )
    confianza = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Confianza del modelo al momento de aceptación'
    )
    motivo = models.TextField(
        help_text='Motivo del cambio de precio'
    )
    fecha_aceptacion = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha y hora de aceptación'
    )
    aceptado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recomendaciones_aceptadas',
        help_text='Usuario que aceptó la recomendación'
    )
    
    class Meta:
        verbose_name = 'Historial de Recomendación'
        verbose_name_plural = 'Historial de Recomendaciones'
        ordering = ['-fecha_aceptacion']
    
    def __str__(self):
        return f'{self.habitacion} - {self.fecha_aceptacion.strftime("%Y-%m-%d")} - {self.tarifa_anterior} → {self.tarifa_nueva}'
    
    @property
    def cambio_porcentaje(self):
        """Calcula el porcentaje de cambio en el precio"""
        if self.tarifa_anterior > 0:
            cambio = ((self.tarifa_nueva - self.tarifa_anterior) / self.tarifa_anterior) * 100
            return round(cambio, 2)
        return 0

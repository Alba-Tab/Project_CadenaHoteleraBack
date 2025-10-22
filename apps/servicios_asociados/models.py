from django.db import models

from apps.reservas.models import Reserva
from apps.servicios.models import Servicio
from apps.folioestancias.models import FolioEstancia

# Modelo para relacionar servicios durante una reserva
class ServiciosAsociados(models.Model):
    servicio = models.ForeignKey(Servicio,on_delete=models.CASCADE,related_name="reservas_servicio")
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='reservas')
    folioestancia = models.ForeignKey(FolioEstancia, on_delete=models.CASCADE, related_name='folioestancias')
    
    cantidad = models.PositiveIntegerField()
    fecha_servicio = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('solicitado', 'Solicitado'),
            ('confirmado', 'Confirmado'),
            ('en_proceso', 'En Proceso'),
            ('completado', 'Completado'),
            ('cancelado', 'Cancelado'),
        ],
        default='solicitado'
    )
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["fecha_servicio"]

    def __str__(self):
        return f"{self.servicio.nombre} - {self.cantidad} unidades"
    
    def save(self, *args, **kwargs):
        # Calcular monto_total = cantidad × precio del servicio
        if self.servicio and self.cantidad:
            self.monto_total = self.cantidad * self.servicio.precio
        super().save(*args, **kwargs)
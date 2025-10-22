from django.db import models

from apps.reservas.models import Reserva
from apps.servicios.models import Servicio
from apps.folioestancias.models import FolioEstancia

# Modelo para relacionar servicios durante una reserva
class ServiciosAsociados(models.Model):
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name="reservas_servicio"
    )
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='reservas')
    folioestancia = models.ForeignKey(FolioEstancia, on_delete=models.CASCADE, related_name='folioestancias')
    cantidad = models.PositiveIntegerField()
    fecha_consumo = models.DateField()

    class Meta:
        ordering = ["fecha_consumo"]

    def __str__(self):
        return f"{self.servicio.nombre} - {self.cantidad} unidades"
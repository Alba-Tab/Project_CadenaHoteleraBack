from django.db import models
from apps.reservas.models import Reserva
from apps.folioestancias.models import FolioEstancia
class Servicio(models.Model):
    nombre = models.CharField(max_length=60)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "servicio"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"
        
# Modelo para relacionar servicios durante una reserva
class ServicioReserva(models.Model):
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name="reservas_servicio"
    )
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='reservas')
    folioestancia = models.ForeignKey(FolioEstancia, on_delete=models.CASCADE, related_name='folioestancias')
    cantidad = models.PositiveIntegerField()
    fecha_consumo = models.DateField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "servicio_reserva"
        ordering = ["fecha_consumo"]

    def __str__(self):
        return f"{self.servicio.nombre} - {self.cantidad} unidades"

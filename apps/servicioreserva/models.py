from django.db import models
# from apps.servicios.models import Servicio
# from apps.reservas.models import Reserva
# from apps.folioestancia.models import Folioestancia


class ServicioReserva(models.Model):

    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='servicios')
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='reservas')
    folioestancia = models.ForeignKey(FolioEstancia, on_delete=models.CASCADE, related_name='folioestancias')

    cantidad = models.PositiveIntegerField()
    fecha_consumo = models.DateField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "ServicioReserva"
        verbose_name_plural = "ServicioReservas"
        unique_together = ['reserva', 'servicio']
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return f'{self.servicio.nombre} - Reserva #{self.reserva.id}'
    
    def save(self, *args, **kwargs):
        # Calcular precio total automáticamente
        if self.cantidad and self.precio_unitario:
            self.precio_total = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
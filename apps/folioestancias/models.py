from django.db import models
from decimal import Decimal

from apps.reservas.models import Reserva
from apps.usuarios.models import User


# Create your models here.
class FolioEstancia(models.Model):
    PENDIENTE = 'Pendiente'
    PAGADO = 'Pagado'

    estado = models.CharField(max_length=100, default=PENDIENTE)   # Pendiente, Pagado, Cancelado
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    huesped = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="folios_estancia",
        null=False,
        blank=False,
    )
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name="folios_estancia",
        null=False,
        blank=False,
    )
    
    def calcular_total_general(self):
        """Calcula el total general del folio (reserva + servicios)"""
        from apps.servicios_asociados.models import ServiciosAsociados
        
        total_reserva = Decimal(self.reserva.total)
        servicios = ServiciosAsociados.objects.filter(folioestancia=self)
        total_servicios = sum(Decimal(s.monto_total) for s in servicios)
        
        return total_reserva + total_servicios
    
    def __str__(self):
        return f"Folio #{self.pk} - {self.huesped.get_full_name()} - {self.estado}"
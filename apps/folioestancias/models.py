from django.db import models

from apps.reservas.models import Reserva
from apps.usuarios.models import User


# Create your models here.
class FolioEstancia(models.Model):
    PENDIENTE = 'Pendiente'
    PAGADO = 'Pagado'
    CANCELADO = 'Cancelado'

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

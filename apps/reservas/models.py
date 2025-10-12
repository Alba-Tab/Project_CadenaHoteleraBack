from django.db import models

from apps.habitaciones.models import Habitacion
from apps.hoteles.models import Hotel
from apps.usuarios.models import User


# Create your models here.
class Reserva(models.Model):
    CONFIRMADA = 'confirmada'
    CANCELADA = 'cancelada'
    PENDIENTE = 'pendiente'
    REALIZADA = 'realizada'

    ESTADO_CHOICES = [
        (CONFIRMADA, 'Confirmada'),
        (CANCELADA, 'Cancelada'),
        (PENDIENTE, 'Pendiente'),
        (REALIZADA, 'Realizada'),
    ]

    fecha_reserva = models.DateField(auto_now_add=True)
    fecha_entrada = models.DateField(null=False, blank=False)
    fecha_salida = models.DateField(null=False, blank=False)
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        blank=False
    )
    estado = models.CharField(
        max_length=50,
        choices=ESTADO_CHOICES,
        default=CONFIRMADA
    ) # e.g., 'confirmada', 'cancelada', etc.
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.CASCADE,
        related_name='reservas',
        null=False,
        blank=False
    )
    huesped = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservas',
        null=False,
        blank=False
    )
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name='reservas',
        null=False,
        blank=False
    )

# class ServicioReserva(models.Model):
#     cantidad = models.PositiveIntegerField(default=1)
#     fecha_comsumo = models.DateField(auto_now_add=True)
#     precio_unitario = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         null=False,
#         blank=False
#     )
#     monto_total = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         null=False,
#         blank=False
#     )
#     reserva = models.ForeignKey(
#         Reserva,
#         on_delete=models.CASCADE,
#         related_name='servicios'
#     )
#     servicio = models.ForeignKey(
#         'servicios.Servicio',
#         on_delete=models.CASCADE,
#         related_name='reservas'
#     )

    # class Meta:
    #     unique_together = ('reserva', 'servicio')

# class DetalleReserva(models.Model):
#     reserva = models.ForeignKey(
#         Reserva,
#         on_delete=models.CASCADE,
#         related_name='habitaciones_reservadas'
#     )
#     habitacion = models.ForeignKey(
#         Habitacion,
#         on_delete=models.CASCADE,
#         related_name='reservas'
#     )
#
#     class Meta:
#         unique_together = ('reserva', 'habitacion')
#
# class ServicioExtra(models.Model):
#     servicio = models.ForeignKey(
#         'servicios.Servicio',
#         on_delete=models.CASCADE,
#         related_name='servicios_extra'
#     )
#     detalle_reserva = models.ForeignKey(
#         DetalleReserva,
#         on_delete=models.CASCADE,
#         related_name='servicios_extra'
#     )
#     cantidad = models.PositiveIntegerField(default=1)
#
#     class Meta:
#         unique_together = ('servicio', 'detalle_reserva')
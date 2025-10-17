from django.db import models
from apps.reservas.models import Reserva

class CheckInOut(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name="checkinout")
    fecha_checkin = models.DateField()
    hora_checkin = models.TimeField()
    fecha_checkout = models.DateField(null=True, blank=True)
    hora_checkout = models.TimeField(null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "check_in_out"
        ordering = ["-fecha_checkin"]

    def __str__(self):
        return f"CheckInOut - Reserva #{self.reserva.id}"
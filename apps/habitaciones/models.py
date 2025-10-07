from django.db import models
from apps.hoteles.models import Hotel  # asegúrate de importar correctamente

class Habitacion(models.Model):
    TIPO_CHOICES = [
        ('individual', 'Individual'),
        ('doble', 'Doble'),
        ('suite', 'Suite'),
    ]

    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('mantenimiento', 'En mantenimiento'),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='habitaciones')
    numero = models.CharField(max_length=10)
    descripcion = models.TextField(blank=True, null=True)
    precio_noche = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')

    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"
        unique_together = ['hotel', 'numero']

    def __str__(self):
        return f'Habitación {self.numero} - {self.hotel.nombre}'

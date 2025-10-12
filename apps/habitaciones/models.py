from django.db import models
from apps.hoteles.models import Hotel  # asegúrate de importar correctamente

class Habitacion(models.Model):
    DISPONIBLE = 'disponible'
    OCUPADA = 'ocupada'
    MANTENIMIENTO = 'mantenimiento'
    RESERVADA = 'reservada'

    TIPO_CHOICES = [
        ('individual', 'Individual'),
        ('doble', 'Doble'),
        ('suite', 'Suite'),
    ]

    ESTADO_CHOICES = [
        (DISPONIBLE, 'Disponible'),
        (OCUPADA, 'Ocupada'),
        (MANTENIMIENTO, 'Mantenimiento'),
        (RESERVADA, 'Reservada'),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='habitaciones')
    numero = models.CharField(max_length=10)
    capacidad = models.CharField(max_length=10)
    descripcion = models.TextField(blank=True, null=True)
    precio_noche = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20)
    tamanio = models.CharField(max_length=10)
    tipo = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"
        unique_together = ['hotel', 'numero']

    def __str__(self):
        return f'Habitación {self.numero} - {self.hotel.nombre}'

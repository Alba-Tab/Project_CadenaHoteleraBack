from django.db import models



class Hotel(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=50)
    pais = models.CharField(max_length=50)
    estado = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Hotel"
        verbose_name_plural = "Hoteles"

    def __str__(self):
        return self.nombre
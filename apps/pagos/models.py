from django.db import models

from django.db import models

class Pago(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_COMPLETADO = "completado"
    ESTADO_FALLIDO = "fallido"
    ESTADOS = [
        (ESTADO_PENDIENTE, "pendiente"),
        (ESTADO_COMPLETADO, "completado"),
        (ESTADO_FALLIDO, "fallido"),
    ]

    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)
    fecha_pago = models.DateField()
    metodo = models.CharField(max_length=50)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    referencia = models.CharField(max_length=100, blank=True, null=True)

    # Referencia al modelo FolioEstancia que está en la app folioestancias
    folio_estancia = models.ForeignKey(
        "folioestancias.FolioEstancia",
        on_delete=models.CASCADE,
        related_name="pagos",
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pago"
        ordering = ["-fecha_pago", "-id"]

    def __str__(self):
        ref = f" ({self.referencia})" if self.referencia else ""
        return f"Pago {self.id} - {self.estado}{ref}"

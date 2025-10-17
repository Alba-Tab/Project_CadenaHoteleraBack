from django.db import models
from apps.folioestancias.models import FolioEstancia


class Pago(models.Model):
    """
    Modelo para gestionar los pagos de los folios de estancia.
    """
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_COMPLETADO = "completado"
    ESTADO_FALLIDO = "fallido"
    
    ESTADOS = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_COMPLETADO, "Completado"),
        (ESTADO_FALLIDO, "Fallido"),
    ]

    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default=ESTADO_PENDIENTE,
        help_text="Estado actual del pago"
    )
    fecha_pago = models.DateField(help_text="Fecha en que se realizó el pago")
    metodo = models.CharField(
        max_length=50,
        help_text="Método de pago utilizado (efectivo, tarjeta, transferencia, etc.)"
    )
    monto = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Monto del pago"
    )
    referencia = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Referencia o número de transacción (opcional)"
    )

    # Relación con FolioEstancia (opcional, pero vinculada)
    folio_estancia = models.ForeignKey(
        FolioEstancia,
        on_delete=models.CASCADE,
        related_name="pagos",
        null=True,
        blank=True,
        help_text="Folio de estancia asociado al pago"
    )

    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pago"
        ordering = ["-fecha_pago", "-id"]
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        indexes = [
            models.Index(fields=['estado', 'fecha_pago']),
            models.Index(fields=['folio_estancia', 'estado']),
        ]

    def __str__(self):
        return f"Pago {self.id} - {self.get_estado_display()} - ${self.monto} - {self.metodo}"
    
    def is_completado(self):
        """Retorna True si el pago está completado."""
        return self.estado == self.ESTADO_COMPLETADO
    
    def is_pendiente(self):
        """Retorna True si el pago está pendiente."""
        return self.estado == self.ESTADO_PENDIENTE
    
    def is_fallido(self):
        """Retorna True si el pago falló."""
        return self.estado == self.ESTADO_FALLIDO

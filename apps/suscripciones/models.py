from django.db import models
from core.models import Tenant
from django.core.validators import MinValueValidator
from django.utils import timezone

class TipoChoices(models.TextChoices):
    MENSUAL = "Mensual", "Mensual"
    ANUAL = "Anual", "Anual"
    TRIMESTRAL = "Trimestral", "Trimestral"

class EstadoChoises(models.TextChoices):
    ACTIVO = "activo", "Activo"
    VENCIDO = "vencido", "Vencido"
    PAUSADO = "pausado", "Pausado"
    CANCELADO = "cancelado", "Cancelado"
    PRUEBA = "prueba", "Prueba"

class Plan(models.Model):
    nombre = models.CharField(max_length=30)
    max_usuarios = models.IntegerField(default=5)
    max_hoteles = models.IntegerField(default=1)
    precio = models.FloatField()
    tipo = models.CharField(max_length=12, choices=TipoChoices.choices)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'tipo'], name='unique_nombre_tipo')
        ]
        ordering = ['nombre', 'tipo']
        return f"{self.nombre} - {self.tipo}"
    

class Suscripcion(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='suscripciones')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=EstadoChoises.choices)
    inicio_periodo = models.DateField()
    fin_periodo = models.DateField()
    
    def __str__(self):
        return f"{self.tenant.schema_name} - {self.plan.nombre} ({self.estado})"
    
    def esta_activa(self):
        """Verifica si la suscripción está activa."""
        return self.estado == "activo"
    
    @property
    def puede_escribir(self) -> bool:
        """Regla mínima para permitir crear recursos."""
        if self.estado in ("activo", "prueba"):
            return self.fin_periodo >= timezone.now().date()
        return False

class UsoTenant(models.Model):
    """
    Contadores materializados por inquilino para validar cuotas con baja latencia
    y sin hacer COUNTs costosos en el esquema del tenant.
    """
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name="uso")
    hoteles = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    usuarios = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    ultima_actualizacion = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Uso de Tenant"
        verbose_name_plural = "Usos de Tenants"
    
    def __str__(self):
        return f"{self.tenant.schema_name} - Hoteles: {self.hoteles}, Usuarios: {self.usuarios}"

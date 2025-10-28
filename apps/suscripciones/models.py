from django.db import models
from core.models import Tenant
from django.core.validators import MinValueValidator
from django.utils import timezone

class TipoChoices(models.TextChoices):
    MENSUAL = "Mensual","mensual"
    ANUAL = "Anual","anual"
    TRIMESTRAL = "T","Trimestral"

class EstadoChoises(models.TextChoices):
    ACTIVO = "activo","activo"
    VENCIDO = "vencido","vencido"
    PAUSADO = "pausado","pausado"
    CANCELADO = "cancelado","cancelado"
    PRUEBA = "prueba","prueba"

class Plan(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    max_users = models.IntegerField(default=5)
    max_hotels = models.IntegerField(default=1)
    precio = models.FloatField()
    Tipo = models.CharField(max_length=12, choices=TipoChoices.choices)
    is_active  = models.BooleanField(default=True)
    

class Suscripcion(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan,on_delete=models.PROTECT)
    status = models.CharField(max_length=20,choices=EstadoChoises.choices)
    inicio_periodo = models.DateField()
    fin_periodo = models.DateField()
    
    def is_active(self):
        return self.status=="activo"
    
    @property
    def is_active_for_writes(self) -> bool:
        """Regla mínima para permitir crear recursos."""
        if self.status in ("activo", "prueba"):
            return self.fin_periodo >= timezone.now()
        return False

class TenantUsage(models.Model):
    """
    Contadores materializados por inquilino para validar cuotas con baja latencia
    y sin hacer COUNTs costosos en el esquema del tenant.
    """
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name="usage")
    hotels = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    users  = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    last_reset = models.DateTimeField(default=timezone.now)

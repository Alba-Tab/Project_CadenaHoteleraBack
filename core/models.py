from django.db import models
from django_tenants.models import TenantMixin

class Tenant(TenantMixin):
    """
    Modelo de Tenant para multitenant basado en headers.
    
    Cada tenant representa una empresa/organización con su propio schema de BD.
    El tenant se identifica por el header X-Tenant

    """
    name = models.CharField(max_length=100, verbose_name="Nombre de la empresa")
    paid_until = models.DateField(null=True, blank=True, verbose_name="Pagado hasta")
    on_trial = models.BooleanField(default=True, verbose_name="En periodo de prueba")
    
    # Configuración de schema
    auto_create_schema = False  # No crear schema automáticamente - se hará en background
    auto_drop_schema = True     # Elimina el schema automáticamente al borrar
    
    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
    
    def __str__(self):
        return f"{self.name} ({self.schema_name})"


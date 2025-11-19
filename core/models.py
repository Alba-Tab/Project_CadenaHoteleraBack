from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Tenant(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField(null=True, blank=True)
    on_trial = models.BooleanField(default=True)
    auto_create_schema = False  # No crear schema automáticamente - se hará en background
    auto_drop_schema = True  # elimina el schema automáticamente al borrar

class Domain(DomainMixin):
    pass


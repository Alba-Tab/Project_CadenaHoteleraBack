from django_tenants.utils import schema_context
from .models import Suscripcion

def get_subscription(tenant):
    with schema_context("public"):
        return Suscripcion.objects.select_related("plan").get(tenant=tenant)
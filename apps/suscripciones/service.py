from django_tenants.utils import schema_context
from django.utils import timezone
from .models import Suscripcion, UsoTenant, Plan

def obtener_suscripcion_activa(tenant):
    """
    Obtiene la suscripción activa más reciente de un tenant.
    
    Args:
        tenant: Objeto Tenant
        
    Returns:
        Suscripcion o None si no existe suscripción activa
    """
    with schema_context("public"):
        return (
            Suscripcion.objects
            .select_related("plan")
            .filter(tenant=tenant, estado__in=["activo", "prueba"])
            .order_by("-fin_periodo")
            .first()
        )


def obtener_uso_tenant(tenant):
    """
    Obtiene o crea el registro de uso de recursos del tenant.
    
    Args:
        tenant: Objeto Tenant
        
    Returns:
        UsoTenant
    """
    with schema_context("public"):
        uso, _ = UsoTenant.objects.get_or_create(tenant=tenant)
        return uso


def validar_puede_crear_hotel(tenant):
    """
    Valida si un tenant puede crear un nuevo hotel según su plan.
    
    Args:
        tenant: Objeto Tenant
        
    Returns:
        tuple (bool, str): (puede_crear, mensaje_error)
    """
    with schema_context("public"):
        suscripcion = obtener_suscripcion_activa(tenant)
        
        if not suscripcion:
            return False, "No existe suscripción activa."
        
        if not suscripcion.puede_escribir:
            return False, "Suscripción inactiva o vencida."
        
        uso = obtener_uso_tenant(tenant)
        
        if uso.hoteles >= suscripcion.plan.max_hoteles:
            return False, f"Límite de hoteles alcanzado ({suscripcion.plan.max_hoteles})."
        
        return True, ""


def validar_puede_crear_usuario(tenant):
    """
    Valida si un tenant puede crear un nuevo usuario según su plan.
    
    Args:
        tenant: Objeto Tenant
        
    Returns:
        tuple (bool, str): (puede_crear, mensaje_error)
    """
    with schema_context("public"):
        suscripcion = obtener_suscripcion_activa(tenant)
        
        if not suscripcion:
            return False, "No existe suscripción activa."
        
        if not suscripcion.puede_escribir:
            return False, "Suscripción inactiva o vencida."
        
        uso = obtener_uso_tenant(tenant)
        
        if uso.usuarios >= suscripcion.plan.max_usuarios:
            return False, f"Límite de usuarios alcanzado ({suscripcion.plan.max_usuarios})."
        
        return True, ""
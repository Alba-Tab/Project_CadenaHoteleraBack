from django_tenants.utils import schema_context
from apps.suscripciones.models import Suscripcion

class SuscripcionMiddleware:
    """
    Middleware que agrega la suscripción activa del tenant al request.
    Se puede acceder mediante: request.suscripcion
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Inicializar suscripcion en None
        request.suscripcion = None
        
        # Obtener el tenant del request
        tenant = getattr(request, "tenant", None)
        
        if tenant:
            # Buscar la suscripción activa más reciente en el esquema público
            with schema_context("public"):
                request.suscripcion = (
                    Suscripcion.objects
                    .select_related("plan")
                    .filter(tenant=tenant, estado__in=["activo", "prueba"])
                    .order_by("-fin_periodo")
                    .first()
                )
        
        return self.get_response(request)

from django_tenants.utils import schema_context
from apps.suscripciones.models import Suscripcion
from django.core.cache import cache

class SuscripcionMiddleware:
    """
    Middleware que agrega la suscripción activa del tenant al request.
    Se puede acceder mediante: request.suscripcion
    OPTIMIZADO: Usa cache para reducir queries a la base de datos
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Inicializar suscripcion en None
        request.suscripcion = None
        
        # Obtener el tenant del request
        tenant = getattr(request, "tenant", None)
        
        if tenant:
            # 🚀 CACHE: Usar cache de 5 minutos para evitar consultas repetidas
            cache_key = f"suscripcion_tenant_{tenant.id}"
            suscripcion = cache.get(cache_key)
            
            if suscripcion is None:
                # Solo hacer la query si no está en cache
                with schema_context("public"):
                    suscripcion = (
                        Suscripcion.objects
                        .select_related("plan")
                        .filter(tenant=tenant, estado__in=["activo", "prueba"])
                        .order_by("-fin_periodo")
                        .first()
                    )
                    # Guardar en cache por 5 minutos (300 segundos)
                    cache.set(cache_key, suscripcion, 300)
            
            request.suscripcion = suscripcion
        
        return self.get_response(request)

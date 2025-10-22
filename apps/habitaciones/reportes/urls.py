from apps._reporting.endpoints import build_urlpatterns_for_registry
from .registry import REGISTRY

urlpatterns = build_urlpatterns_for_registry(REGISTRY)


# monta endpoints de esta app:
# GET /api/habitaciones/reportes/
# GET /api/habitaciones/reportes/{slug}/schema
# POST /api/habitaciones/reportes/{slug}/preview
# POST /api/habitaciones/reportes/{slug}/export
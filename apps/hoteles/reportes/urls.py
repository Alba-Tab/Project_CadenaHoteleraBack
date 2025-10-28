from apps._reporting.endpoints import build_urlpatterns_for_registry
from .registry import REGISTRY


urlpatterns = build_urlpatterns_for_registry(REGISTRY)

# monta endpoints de esta app:
# GET /api/hoteles/reportes/
# GET /api/hoteles/reportes/{slug}/schema
# POST /api/hoteles/reportes/{slug}/preview
# POST /api/hoteles/reportes/{slug}/export
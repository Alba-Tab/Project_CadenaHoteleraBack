from apps._reporting.endpoints import build_urlpatterns_for_registry
from .registry import REGISTRY

urlpatterns = build_urlpatterns_for_registry(REGISTRY)


# levanta endpoints solo de pagos:
# GET /api/pagos/reportes/
# GET /api/pagos/reportes/{slug}/schema
# POST /api/pagos/reportes/{slug}/preview
# POST /api/pagos/reportes/{slug}/export
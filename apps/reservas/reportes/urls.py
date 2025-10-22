# from django.urls import urlpatterns as _urls  # evitar shadow
from apps._reporting.endpoints import build_urlpatterns_for_registry
from .registry import REGISTRY

urlpatterns = build_urlpatterns_for_registry(REGISTRY)


#Genera los endpoints de esa app:
# GET /api/reservas/reportes/
# GET /api/reservas/reportes/{slug}/schema
# POST /api/reservas/reportes/{slug}/preview
# POST /api/reservas/reportes/{slug}/export
from django.urls import path
from apps._reporting.endpoints import build_views_for_registry
from .registry import REGISTRY
from .views import ReservasReportEmailView

# Generar las vistas base
ListV, SchemaV, PreviewV, ExportV = build_views_for_registry(REGISTRY)

# Usar vistas base para list, schema, preview y export; personalizada para email
urlpatterns = [
    path('', ListV.as_view(), name='reservas-report-list'),
    path('<slug:slug>/schema', SchemaV.as_view(), name='reservas-report-schema'),
    path('<slug:slug>/preview', PreviewV.as_view(), name='reservas-report-preview'),
    path('<slug:slug>/export', ExportV.as_view(), name='reservas-report-export'),
    path('<slug:slug>/email', ReservasReportEmailView.as_view(), name='reservas-report-email'),
]


# Genera los endpoints de esta app:
# GET /api/reservas/reportes/
# GET /api/reservas/reportes/{slug}/schema
# POST /api/reservas/reportes/{slug}/preview
# POST /api/reservas/reportes/{slug}/export
# POST /api/reservas/reportes/{slug}/email

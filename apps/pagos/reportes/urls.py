from django.urls import path
from apps._reporting.endpoints import build_views_for_registry
from .registry import REGISTRY
from .views import PagosReportEmailView

# Generar las vistas base
ListV, SchemaV, PreviewV, ExportV = build_views_for_registry(REGISTRY)

# Usar vistas base para list, schema, preview y export; personalizada para email
urlpatterns = [
    path('', ListV.as_view(), name='pagos-report-list'),
    path('<slug:slug>/schema', SchemaV.as_view(), name='pagos-report-schema'),
    path('<slug:slug>/preview', PreviewV.as_view(), name='pagos-report-preview'),
    path('<slug:slug>/export', ExportV.as_view(), name='pagos-report-export'),
    path('<slug:slug>/email', PagosReportEmailView.as_view(), name='pagos-report-email'),
]


# levanta endpoints solo de pagos:
# GET /api/pagos/reportes/
# GET /api/pagos/reportes/{slug}/schema
# POST /api/pagos/reportes/{slug}/preview
# POST /api/pagos/reportes/{slug}/export
# POST /api/pagos/reportes/{slug}/email

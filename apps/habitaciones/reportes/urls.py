from django.urls import path
from apps._reporting.endpoints import build_views_for_registry
from .registry import REGISTRY
from .views import (
    HabitacionesReportPreviewView,
    HabitacionesReportExportView,
    HabitacionesReportEmailView
)

# Generar las vistas base (list y schema)
ListV, SchemaV, _, _ = build_views_for_registry(REGISTRY)

# Usar vistas personalizadas para preview, export y email
urlpatterns = [
    path('', ListV.as_view(), name='habitaciones-report-list'),
    path('<slug:slug>/schema', SchemaV.as_view(), name='habitaciones-report-schema'),
    path('<slug:slug>/preview', HabitacionesReportPreviewView.as_view(), name='habitaciones-report-preview'),
    path('<slug:slug>/export', HabitacionesReportExportView.as_view(), name='habitaciones-report-export'),
    path('<slug:slug>/email', HabitacionesReportEmailView.as_view(), name='habitaciones-report-email'),
]


# monta endpoints de esta app:
# GET /api/habitaciones/reportes/
# GET /api/habitaciones/reportes/{slug}/schema
# POST /api/habitaciones/reportes/{slug}/preview  (con soporte para porcentaje_ocupacion)
# POST /api/habitaciones/reportes/{slug}/export   (con soporte para porcentaje_ocupacion)
# POST /api/habitaciones/reportes/{slug}/email    (con soporte para porcentaje_ocupacion)
# POST /api/habitaciones/reportes/{slug}/export   (con soporte para porcentaje_ocupacion)

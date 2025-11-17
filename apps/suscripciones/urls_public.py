"""
URLs para suscripciones - Esquema PÚBLICO
Estas rutas permiten:
1. Ver planes disponibles (sin autenticación) - /api/planes/
2. Gestionar planes (solo admin) - /api/admin/planes/
3. Crear nuevas suscripciones (registro de tenants)
4. Gestionar suscripciones (admin)
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlanPublicoViewSet, PlanAdminViewSet, SuscripcionPublicaViewSet

# Router para endpoints públicos
public_router = DefaultRouter()
public_router.register('planes', PlanPublicoViewSet, basename='plan-publico')
public_router.register('suscripciones', SuscripcionPublicaViewSet, basename='suscripcion-publica')

# Router para endpoints de administración
admin_router = DefaultRouter()
admin_router.register('planes', PlanAdminViewSet, basename='plan-admin')

urlpatterns = [
    path('', include(public_router.urls)),
    path('admin/', include(admin_router.urls)),
]

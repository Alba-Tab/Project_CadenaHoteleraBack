"""
URLs para suscripciones - Esquema PÚBLICO
Estas rutas permiten:
1. Ver planes disponibles (sin autenticación)
2. Crear nuevas suscripciones (registro de tenants)
3. Gestionar suscripciones (admin)
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlanPublicoViewSet, SuscripcionPublicaViewSet

router = DefaultRouter()
router.register('planes', PlanPublicoViewSet, basename='plan-publico')
router.register('suscripciones', SuscripcionPublicaViewSet, basename='suscripcion-publica')

urlpatterns = [
    path('', include(router.urls)),
]

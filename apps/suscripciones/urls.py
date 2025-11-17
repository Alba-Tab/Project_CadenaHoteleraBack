"""
URLs para suscripciones - Esquema del TENANT
Estas rutas permiten que cada tenant vea SU propia suscripción.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MiSuscripcionViewSet

router = DefaultRouter()
router.register('mi-suscripcion', MiSuscripcionViewSet, basename='mi-suscripcion')

urlpatterns = [
    path('', include(router.urls)),
]

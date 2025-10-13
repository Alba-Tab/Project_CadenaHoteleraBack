from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServicioReservaViewSet


router = DefaultRouter()
router.register(r'', ServicioReservaViewSet, basename='servicioreserva')

urlpatterns = [
    path('', include(router.urls)),
]

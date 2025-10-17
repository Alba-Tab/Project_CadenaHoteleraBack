from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServicioViewSet, ServicioReservaViewSet

router = DefaultRouter()
router.register(r"servicios", ServicioViewSet, basename="servicio")
router.register(r"servicioreservas", ServicioReservaViewSet, basename="servicioreserva")

urlpatterns = [
    path("", include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServicioViewSet

router = DefaultRouter()
router.register(r"servicios", ServicioViewSet, basename="servicio")

urlpatterns = [
    path("", include(router.urls)),
]

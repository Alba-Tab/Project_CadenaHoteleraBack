from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServicioViewSet

router = DefaultRouter()
router.register(r"", ServicioViewSet, basename="servicio")

urlpatterns = [
    path("", include(router.urls)),
    path("reportes/", include('apps.servicios.reportes.urls')),
]

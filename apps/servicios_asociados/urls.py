from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiciosAsociadosViewSet

router = DefaultRouter()
router.register(r"serviciosasociados", ServiciosAsociadosViewSet, basename="serviciosasociados")

urlpatterns = [
    path("", include(router.urls)),
]

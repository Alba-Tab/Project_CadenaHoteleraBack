from django.urls import path ,include
from rest_framework.routers import DefaultRouter

from apps.configuracion_apariencia.views import ConfiguracionAparienciaViewSet






router = DefaultRouter()
router.register(r'', ConfiguracionAparienciaViewSet, basename="configuracion-apariencia")

urlpatterns = [
   path('', include(router.urls)),
]

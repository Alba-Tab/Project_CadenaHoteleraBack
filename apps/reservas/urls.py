from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.reservas.views import ReservaViewSet

router = DefaultRouter()
router.register(r'', ReservaViewSet, basename='reservas')

urlpatterns = [
    path('', include(router.urls)),
    path('reportes/', include('apps.reservas.reportes.urls')),
]
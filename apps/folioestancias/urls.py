from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import FolioEstanciaViewSet

router = DefaultRouter()
router.register(r'', FolioEstanciaViewSet, basename='folioestancia')

urlpatterns = [
    path('', include(router.urls)),
    path('reportes/', include('apps.folioestancias.reportes.urls')),
]
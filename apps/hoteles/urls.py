from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet

router = DefaultRouter()
router.register(r'hoteles', HotelViewSet, basename='hotel')  # esto apunta a /api/hoteles/

urlpatterns = [
    path('', include(router.urls)),
]
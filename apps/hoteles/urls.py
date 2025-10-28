from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet

router = DefaultRouter()
router.register('hoteles', HotelViewSet, basename='hotel') 


urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitacionViewSet

router = DefaultRouter()
router.register(r'', HabitacionViewSet, basename='habitacion')

urlpatterns = [
    path('', include(router.urls)),
]

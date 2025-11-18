from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecomendacionIAViewSet

router = DefaultRouter()
router.register(r'recomendar', RecomendacionIAViewSet, basename='recomendacion-ia')

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.habitaciones.reportes.views import RecomendacionPrecioHabitacionesView
from .views import HabitacionViewSet

router = DefaultRouter()
router.register(r'', HabitacionViewSet, basename='habitacion')

urlpatterns = [
     path("recomendaciones-precio/",RecomendacionPrecioHabitacionesView.as_view(),name="habitaciones-recomendaciones-precio",),
    path('', include(router.urls)),
]

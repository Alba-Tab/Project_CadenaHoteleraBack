from django.urls import path, include
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('api/', include('apps.hoteles.urls')),
    path("", include("apps.usuarios.urls")),
    # path('api/hoteles/', include('apps.hoteles.urls')),
    path('api/habitaciones/', include('apps.habitaciones.urls')),
]


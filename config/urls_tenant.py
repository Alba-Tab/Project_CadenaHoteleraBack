from django.urls import path, include
from rest_framework.routers import DefaultRouter

from django.contrib import admin

urlpatterns = [
    path('api/', include('apps.hoteles.urls')),
    path('api/', include("apps.usuarios.urls")),
    # path('api/hoteles/', include('apps.hoteles.urls')),
    path('api/habitaciones/', include('apps.habitaciones.urls')),
    path('api/reservas/', include('apps.reservas.urls')),
    #
    path('admin/', admin.site.urls),
]


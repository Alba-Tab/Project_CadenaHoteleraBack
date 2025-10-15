from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib import admin

urlpatterns = [
    path('api/', include('apps.hoteles.urls')),
    path('api/', include("apps.usuarios.urls")),
    #path('api/hoteles/', include('apps.hoteles.urls')),
    path('api/habitaciones/', include('apps.habitaciones.urls')),
    path("api/", include("apps.servicios.urls")),# incluye servicios y servicioreservas
    path('api/reservas/', include('apps.reservas.urls')),
    path('api/folioestancias/', include('apps.folioestancias.urls')),
    path('api/fidelizacion/', include('apps.fidelizacion.urls')),
    path('api/checkinout/', include('apps.checkinout.urls')),
    #añadi ests 2 para probar login si estorba, solo borrenlas
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #
    path('admin/', admin.site.urls),
]


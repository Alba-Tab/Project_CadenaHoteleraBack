from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib import admin

urlpatterns = [

    #ruta reportes para usuarios (No mover el orden de estos 2!)
    path('api/usuarios/reportes/', include('apps.usuarios.reportes.urls')),
    path('api/', include("apps.usuarios.urls")),

    #ruta reportes para habitaciones (No mover el orden de estos 2!)
    path('api/habitaciones/reportes/', include('apps.habitaciones.reportes.urls')),
    path('api/habitaciones/', include('apps.habitaciones.urls')),

    #ruta reportes para reservas (No mover el orden de estos 2!)
    path('api/reservas/reportes/', include('apps.reservas.reportes.urls')),
    path('api/reservas/', include('apps.reservas.urls')),

    #ruta reportes para hoteles (No mover el orden de estos 2!)
    path("api/hoteles/reportes/", include("apps.hoteles.reportes.urls")),
    path('api/hoteles/', include('apps.hoteles.urls')),
    # path('api/', include('apps.hoteles.urls')),

    #ruta reportes para pagos (No mover el orden de estos 2!)
    path('api/pagos/reportes/', include('apps.pagos.reportes.urls')),
    path('api/', include('apps.pagos.urls')),
    
    # path("api/", include("apps.servicios.urls")),# incluye servicios y servicioreservas
    #ruta reportes para servicios (No mover el orden de estos 2!)
    path("api/servicios/reportes/", include("apps.servicios.reportes.urls")),
    path("api/servicios/", include("apps.servicios.urls")),
    
    path("api/servicios-asociados/", include("apps.servicios_asociados.urls")),

    path('api/folioestancias/', include('apps.folioestancias.urls')),
    path('api/fidelizacion/', include('apps.fidelizacion.urls')),
    path('api/checkinout/', include('apps.checkinout.urls')),

    # Machine Learning - Recomendaciones de precios
    path('api/ia/', include('apps.recomendaciones_ia.urls')),

    path('api/', include('apps.suscripciones.urls')),  # 🔹 Rutas de suscripciones
    path('api/configuracion-apariencia/', include('apps.configuracion_apariencia.urls')),
    path('api/', include('apps.facial_recognition.urls')),  # 🔹 Reconocimiento facial
    #añadi ests 2 para probar login si estorba, solo borrenlas
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),#ebcargado de la auditoria

]


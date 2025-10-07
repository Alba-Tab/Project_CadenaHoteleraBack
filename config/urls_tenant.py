from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()


urlpatterns = [
    path("api/", include(router.urls)),
<<<<<<< HEAD
    path('api/hoteles/', include('apps.hoteles.urls')),
    path('api/habitaciones/', include('apps.habitaciones.urls')),
=======
    path("", include("apps.usuarios.urls")),
>>>>>>> 6f8bfe4b2419cf590364055582ac229333123b19
]

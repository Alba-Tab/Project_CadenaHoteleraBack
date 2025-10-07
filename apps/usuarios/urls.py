from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.usuarios.views import UserViewSet

router = DefaultRouter()
router.register("usuarios", UserViewSet, basename="usuario")

urlpatterns = router.urls
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.usuarios.views import UserViewSet, RoleViewSet, PermissionViewSet

router = DefaultRouter()
router.register("usuarios", UserViewSet, basename="usuario")
router.register("roles", RoleViewSet, basename="role")
router.register("permisos", PermissionViewSet, basename="permiso")

urlpatterns = [
    path("", include(router.urls)),
    path("reportes/", include('apps.usuarios.reportes.urls')),  # ← Nueva línea
]

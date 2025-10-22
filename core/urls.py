from rest_framework.routers import DefaultRouter
from .views import TenantViewSet,TenantFormViewSet,PublicSchemaView
from django.urls import path
from .views_audit import AuditLogViewSet

router = DefaultRouter()
router.register("tenants", TenantViewSet, basename="tenant")
router.register("tenants-forms", TenantFormViewSet, basename="tenant-form")
router.register("auditoria", AuditLogViewSet, basename="auditoria")

urlpatterns = [
    path("tenants-public/", PublicSchemaView.as_view(), name="tenant-public"),  # ← APIView
] + router.urls

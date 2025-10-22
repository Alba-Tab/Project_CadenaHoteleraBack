from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import schema_context
from core.audit_registry import register_audit_models

class TenantAuditLogMiddleware(MiddlewareMixin):
    _initialized_tenants = set()

    def process_request(self, request):
        tenant = getattr(request, "tenant", None)
        if tenant and tenant.schema_name not in self._initialized_tenants:
            with schema_context(tenant.schema_name):
                register_audit_models()
                print(f"Auditoría inicializada para schema: {tenant.schema_name}")
            self._initialized_tenants.add(tenant.schema_name)
        return None

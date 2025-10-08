from django.db import connection
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class tenantDebugMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print(">>> Host recibido:", request.get_host())
        print(">>> Esquema activo:", connection.schema_name)
        print(">>> URLConf actual:", getattr(request, "urlconf", settings.ROOT_URLCONF))
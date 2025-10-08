from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.db import connection

class ForcetenantUrlconfMiddleware(MiddlewareMixin):
    """
    Asegura que Django use el URLConf correcto según el esquema activo.
    Si el esquema es 'public' -> usa PUBLIC_SCHEMA_URLCONF.
    Si es cualquier otro -> usa Tenant_URLCONF.
    """

    def process_request(self, request):
        schema = connection.schema_name
        if schema != "public":
            request.urlconf = settings.TENANT_URLCONF
        else:
            request.urlconf = settings.PUBLIC_SCHEMA_URLCONF

        # Para depuración opcional:
        print(f">>> [ForceURLConf] schema={schema} → urlconf={request.urlconf}")
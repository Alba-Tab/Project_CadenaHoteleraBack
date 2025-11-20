"""
Middleware para manejar identificación de tenant mediante headers HTTP.

Este middleware es necesario cuando se usa App Runner detrás de CloudFront,
ya que App Runner no soporta subdominios nativamente.

El frontend debe enviar el header 'X-Tenant-Domain' con el subdominio del tenant.
Por ejemplo: X-Tenant-Domain: hotel1

CloudFront también puede configurarse para extraer el subdominio del Host
y reenviarlo como header personalizado.
"""
from django.http import Http404
from django.conf import settings


class TenantHeaderMiddleware:
    """
    Middleware que extrae el tenant desde un header HTTP personalizado.

    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Intentar obtener el tenant del header X-Tenant-Domain
        tenant_domain = request.headers.get('X-Tenant-Domain', '').strip().lower()
        
        # También intentar desde el query parameter (útil para testing)
        if not tenant_domain:
            tenant_domain = request.GET.get('tenant', '').strip().lower()
        
        # Si encontramos el tenant en el header, modificar el HTTP_HOST
        # para que django-tenants pueda procesarlo correctamente
        if tenant_domain:
            base_domain = settings.TENANT_BASE_DOMAIN
            
            # Construir el dominio completo: tenant.base_domain
            full_domain = f"{tenant_domain}.{base_domain}"
            
            # Modificar el request para que django-tenants lo procese
            request.META['HTTP_HOST'] = full_domain
            request.META['SERVER_NAME'] = full_domain
            
            # Guardar el tenant original para uso posterior
            request.tenant_from_header = tenant_domain
        
        response = self.get_response(request)
        return response


class TenantFromOriginMiddleware:
    """
    Middleware alternativo que extrae el tenant del header Origin.
    
    Útil cuando el frontend envía el subdominio en el header Origin.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Obtener el Origin header (ej: https://hotel1.tudominio.com)
        origin = request.headers.get('Origin', '')
        
        if origin:
            try:
                # Extraer el dominio del origin
                from urllib.parse import urlparse
                parsed = urlparse(origin)
                hostname = parsed.hostname or ''
                
                # Extraer el subdominio (primera parte antes del primer punto)
                parts = hostname.split('.')
                if len(parts) >= 2:
                    tenant_domain = parts[0]
                    base_domain = settings.TENANT_BASE_DOMAIN
                    
                    # Construir el dominio completo
                    full_domain = f"{tenant_domain}.{base_domain}"
                    
                    # Modificar el request
                    request.META['HTTP_HOST'] = full_domain
                    request.META['SERVER_NAME'] = full_domain
                    request.tenant_from_origin = tenant_domain
            except Exception as e:
                # Si hay error, simplemente continuar sin modificar
                pass
        
        response = self.get_response(request)
        return response

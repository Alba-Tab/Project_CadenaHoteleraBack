"""
MIDDLEWARE PARA MULTITENANT BASADO EN HEADERS (X-Tenant)
FUNCIONAMIENTO:
1. Lee el header X-Tenant de cada request
2. Verifica si la ruta es pública (no requiere tenant)
3. Para rutas privadas: valida tenant y cambia de schema
4. Usa connection.set_schema() de django-tenants internamente
"""

from django.http import JsonResponse
from django.db import connection
from django_tenants.utils import get_tenant_model


class TenantHeaderMiddleware:
    """
    Middleware que identifica el tenant mediante el header X-Tenant
    y delega el cambio de schema a Django Tenants.
    """
    
    # ⚡ RUTAS PÚBLICAS - NO requieren tenant (usan schema 'public')
    PUBLIC_ROUTES = [
        '/api/public/',       
        '/api/debug/',        
        '/admin/',            
        '/static/',     
        '/media/',         
        '/health/',               
        '/api/suscripciones/',   
        '/api/planes/', 
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.TenantModel = get_tenant_model()
    
    def __call__(self, request):
        """
        Procesa cada request:
        1. Identifica si es ruta pública o privada
        2. Para rutas privadas: valida y establece el tenant
        3. Para rutas públicas: usa schema 'public'
        """
        
        # 🔍 Verificar si es ruta pública
        if self._is_public_route(request.path):
            # Rutas públicas usan el schema 'public'
            connection.set_schema('public')
            request.tenant = None
            # Usar URLconf público
            request.urlconf = 'config.urls_public'
            return self.get_response(request)
        
        # 🏨 Para rutas privadas: requiere X-Tenant
        tenant_code = request.headers.get('X-Tenant', '').strip().lower()
        
        if not tenant_code:
            return JsonResponse({
                'error': 'Tenant requerido',
                'detail': 'El header X-Tenant es obligatorio para esta ruta',
                'code': 'TENANT_REQUIRED'
            }, status=400)
        
        # ✅ Validar formato del tenant
        if not self._is_valid_tenant_code(tenant_code):
            return JsonResponse({
                'error': 'Formato de tenant inválido',
                'detail': 'El código de tenant debe contener solo letras, números y guiones',
                'code': 'INVALID_TENANT_FORMAT'
            }, status=400)
        
        # 🔍 Buscar el tenant en la base de datos
        try:
            tenant = self.TenantModel.objects.get(schema_name=tenant_code)
        except self.TenantModel.DoesNotExist:
            return JsonResponse({
                'error': 'Tenant no encontrado',
                'detail': f'El tenant "{tenant_code}" no existe en el sistema',
                'code': 'TENANT_NOT_FOUND'
            }, status=404)
        
        # 🎯 Cambiar al schema del tenant usando django-tenants
        try:
            connection.set_schema(tenant.schema_name)
            request.tenant = tenant
            # Usar URLconf de tenant
            request.urlconf = 'config.urls_tenant'
            
        except Exception as e:
            return JsonResponse({
                'error': 'Error al cambiar de schema',
                'detail': str(e),
                'code': 'SCHEMA_SWITCH_ERROR'
            }, status=500)
        
        # Continuar con el request
        response = self.get_response(request)
        
        # Asegurar que el schema se limpia después del request
        connection.set_schema_to_public()
        
        return response
    
    def _is_public_route(self, path):
        return any(path.startswith(route) for route in self.PUBLIC_ROUTES)
    
    def _is_valid_tenant_code(self, tenant_code):
        
        import re
        pattern = r'^[a-z0-9_-]+$'
        return bool(re.match(pattern, tenant_code))

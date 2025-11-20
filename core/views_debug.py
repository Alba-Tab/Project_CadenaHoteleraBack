"""
Vista de debug para verificar el schema activo y configuración del tenant.

Este endpoint ayuda a validar que el middleware multitenant funciona correctamente.
"""

from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def debug_schema_view(request):
    """
    Endpoint de debug que muestra información del schema actual.
    
    Acceso:
    - GET /api/debug/schema/
    
    Headers opcionales:
    - X-Tenant: Código del tenant
    
    Respuesta:
    - schema_name: Nombre del schema PostgreSQL activo
    - tenant_info: Información del tenant (si aplica)
    - is_public: Si está usando el schema público
    - connection_info: Info de la conexión
    """
    
    # Obtener schema actual de la conexión
    current_schema = connection.schema_name
    
    # Información del tenant si existe
    tenant_info = None
    if hasattr(request, 'tenant') and request.tenant:
        tenant_info = {
            'schema_name': request.tenant.schema_name,
            'name': request.tenant.name,
            'on_trial': request.tenant.on_trial,
            'paid_until': str(request.tenant.paid_until) if request.tenant.paid_until else None,
        }
    
    # Headers recibidos
    headers_received = {
        'X-Tenant': request.headers.get('X-Tenant', 'No enviado'),
        'Authorization': 'Presente' if request.headers.get('Authorization') else 'No presente',
    }
    
    # Información de la conexión
    connection_info = {
        'database': connection.settings_dict.get('NAME'),
        'user': connection.settings_dict.get('USER'),
        'host': connection.settings_dict.get('HOST'),
        'port': connection.settings_dict.get('PORT'),
    }
    
    return JsonResponse({
        'status': 'success',
        'message': 'Middleware multitenant funcionando correctamente',
        'schema': {
            'current': current_schema,
            'is_public': current_schema == 'public',
        },
        'tenant': tenant_info,
        'headers': headers_received,
        'connection': connection_info,
        'path': request.path,
        'method': request.method,
    })


@csrf_exempt
@require_http_methods(["GET"])
def debug_test_query(request):
    """
    Endpoint para probar queries en el schema actual.
    
    ⚠️ Solo para desarrollo - eliminar en producción.
    """
    from django.contrib.auth import get_user_model
    from core.models import Tenant
    
    User = get_user_model()
    
    try:
        # Contar usuarios en el schema actual
        user_count = User.objects.count()
        
        # Información del schema
        current_schema = connection.schema_name
        
        # Contar todos los tenants (desde public)
        connection.set_schema('public')
        tenant_count = Tenant.objects.count()
        connection.set_schema(current_schema)
        
        return JsonResponse({
            'status': 'success',
            'current_schema': current_schema,
            'users_in_current_schema': user_count,
            'total_tenants': tenant_count,
            'message': 'Query ejecutada correctamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'current_schema': connection.schema_name,
        }, status=500)

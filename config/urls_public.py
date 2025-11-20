from django.urls import path, include
from django.http import JsonResponse
from django.contrib import admin

def health_check(request):
    """Endpoint de salud para App Runner health checks"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Backend multitenant funcionando correctamente'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", health_check),  # Health check para App Runner
    path("health/", health_check),  # Alternativa
    # 🔹 Rutas públicas para suscripciones (crear suscripciones, ver planes)
    path("api/", include("apps.suscripciones.urls_public")),
    path("api/public/", include("core.urls")),
    path("api/backups/", include("apps.backups.urls")),  # ✅ URLs de backups

]




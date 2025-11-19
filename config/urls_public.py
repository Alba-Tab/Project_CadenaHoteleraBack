from django.urls import path, include
from django.http import HttpResponse, JsonResponse
from django.contrib import admin

<<<<<<< HEAD
def health_check(request):
    """Endpoint de salud para App Runner health checks"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Backend multitenant funcionando correctamente'
    })
=======
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )
>>>>>>> a9f00142f9446800a31cce7a60d111f51d53313b

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", health_check),  # Health check para App Runner
    path("health/", health_check),  # Alternativa
    # 🔹 Rutas públicas para suscripciones (crear suscripciones, ver planes)
    path("api/", include("apps.suscripciones.urls_public")),
    path("api/public/", include("core.urls")),
    path("api/backups/", include("apps.backups.urls")),  # ✅ URLs de backups
    
    
     # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]




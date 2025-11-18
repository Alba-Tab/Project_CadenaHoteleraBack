from django.urls import path, include
from django.http import HttpResponse
from django.contrib import admin

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", lambda r: HttpResponse("Página pública principal")),
    # 🔹 Rutas públicas para suscripciones (crear suscripciones, ver planes)
    path("api/", include("apps.suscripciones.urls_public")),
    path("api/public/", include("core.urls")),
    path("api/backups/", include("apps.backups.urls")),  # ✅ URLs de backups
    
    
     # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]




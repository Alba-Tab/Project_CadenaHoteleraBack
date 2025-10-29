from django.urls import path, include
from django.http import HttpResponse
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

urlpatterns = [
    path("", lambda r: HttpResponse("Página pública principal")),
    path("api/suscripcion/", lambda r: HttpResponse("Detalles de planes y registro de hoteles")),
    path("api/public/", include("core.urls")),
    path("api/backups/", include("apps.backups.urls")),  # ✅ URLs de backups
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

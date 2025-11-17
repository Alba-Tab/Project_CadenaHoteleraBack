from django.urls import path, include
from django.http import HttpResponse
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", lambda r: HttpResponse("Página pública principal")),
    # 🔹 Rutas públicas para suscripciones (crear suscripciones, ver planes)
    path("api/", include("apps.suscripciones.urls_public")),
    path("api/public/", include("core.urls")),
]

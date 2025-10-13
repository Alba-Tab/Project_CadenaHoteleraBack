from django.urls import path, include
from django.http import HttpResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    path("", lambda r: HttpResponse("Página pública principal")),
    path("suscripcion/", lambda r: HttpResponse("Detalles de planes y registro de hoteles")),
    path("public/", include("core.urls")),

    path('api/', include('apps.hoteles.urls')),
    path("", include("apps.usuarios.urls")),
    path('api/habitaciones/', include('apps.habitaciones.urls')),
    path('api/reservas/', include('apps.reservas.urls')),
]

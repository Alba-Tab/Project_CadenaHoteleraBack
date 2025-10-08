from django.urls import path, include
from django.http import HttpResponse

urlpatterns = [
    path("", lambda r: HttpResponse("Página pública principal")),
    path("suscripcion/", lambda r: HttpResponse("Detalles de planes y registro de hoteles")),
    path("", include("core.urls")),
]

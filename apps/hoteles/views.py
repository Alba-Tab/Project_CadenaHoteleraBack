from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from django_tenants.utils import schema_context
from .models import Hotel
from .serializers import HotelSerializer
from core.permissions import EscrituraPermitida, DentroDeCuota
from apps.suscripciones.models import UsoTenant

class HotelViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar hoteles con validación de suscripciones y cuotas.
    """
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    creando_hoteles = True
    permission_classes = [EscrituraPermitida, DentroDeCuota]
    
    def initial(self, request, *args, **kwargs):
        """
        Agrega contadores de recursos al request para validación de cuotas.
        """
        request.contadores_tenant = {
            "hoteles": Hotel.objects.count(),
            "usuarios": self._contar_usuarios()
        }
        return super().initial(request, *args, **kwargs)

    def _contar_usuarios(self):
        """Cuenta los usuarios en el esquema del tenant actual."""
        from apps.usuarios.models import User
        return User.objects.count()

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Crea un hotel validando y actualizando el contador de uso del tenant.
        """
        tenant = self.request.tenant
        suscripcion = self.request.suscripcion
        
        # Validar que existe suscripción activa
        if not suscripcion or not suscripcion.puede_escribir:
            raise PermissionDenied("Suscripción inactiva o vencida.")
        
        # Reservar cupo en el esquema público de forma atómica
        with schema_context("public"):
            uso, _ = UsoTenant.objects.select_for_update().get_or_create(tenant=tenant)
            
            # Validar que no se exceda el límite del plan
            if uso.hoteles >= suscripcion.plan.max_hoteles:
                raise PermissionDenied(
                    f"Límite de hoteles alcanzado ({suscripcion.plan.max_hoteles}). "
                    f"Actualiza tu plan para crear más hoteles."
                )
            
            # Incrementar el contador
            uso.hoteles += 1
            uso.save()
        
        # Intentar crear el hotel
        try:
            serializer.save()
        except Exception as e:
            # Si falla, revertir el contador
            with schema_context("public"):
                uso = UsoTenant.objects.select_for_update().get(tenant=tenant)
                uso.hoteles = max(0, uso.hoteles - 1)
                uso.save()
            raise
    
    @transaction.atomic
    def perform_destroy(self, instance):
        """
        Elimina un hotel y decrementa el contador de uso del tenant.
        """
        tenant = self.request.tenant
        
        # Eliminar el hotel
        instance.delete()
        
        # Decrementar el contador en el esquema público
        with schema_context("public"):
            uso = UsoTenant.objects.select_for_update().get(tenant=tenant)
            uso.hoteles = max(0, uso.hoteles - 1)
            uso.save()
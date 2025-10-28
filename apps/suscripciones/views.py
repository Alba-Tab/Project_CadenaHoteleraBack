from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_tenants.utils import schema_context
from .models import Plan, Suscripcion, UsoTenant
from .serializers import (
    PlanSerializer, 
    SuscripcionSerializer, 
    UsoTenantSerializer,
    EstadisticasUsoSerializer
)


class PlanPublicoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet público para consultar planes disponibles.
    NO requiere autenticación - accesible desde urls_public.py
    """
    queryset = Plan.objects.filter(activo=True)
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]


class SuscripcionPublicaViewSet(viewsets.ModelViewSet):
    """
    ViewSet público para CREAR suscripciones (registro de nuevos tenants).
    Accesible desde urls_public.py para el proceso de registro.
    """
    serializer_class = SuscripcionSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Siempre en esquema público."""
        return Suscripcion.objects.select_related('plan', 'tenant')
    
    def perform_create(self, serializer):
        """Crea suscripción en esquema público."""
        suscripcion = serializer.save()
        
        # Crear el registro de uso para el tenant
        UsoTenant.objects.get_or_create(tenant=suscripcion.tenant)


class MiSuscripcionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para que cada tenant vea SU propia suscripción.
    Accesible desde urls_tenant.py (requiere autenticación).
    """
    serializer_class = SuscripcionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Retorna solo las suscripciones del tenant actual.
        Accede al esquema público porque Suscripcion está en SHARED_APPS.
        """
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
            with schema_context("public"):
                return Suscripcion.objects.filter(tenant=tenant).select_related('plan')
        return Suscripcion.objects.none()
    
    @action(detail=False, methods=['get'])
    def actual(self, request):
        """
        Retorna la suscripción activa actual del tenant.
        GET /api/mi-suscripcion/actual/
        """
        suscripcion = getattr(request, 'suscripcion', None)
        
        if not suscripcion:
            return Response(
                {"detail": "No existe suscripción activa para este tenant."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Ya está en contexto público gracias al middleware
        serializer = self.get_serializer(suscripcion)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Retorna estadísticas de uso del tenant con su suscripción.
        GET /api/mi-suscripcion/estadisticas/
        """
        tenant = getattr(request, 'tenant', None)
        suscripcion = getattr(request, 'suscripcion', None)
        
        if not tenant or not suscripcion:
            return Response(
                {"detail": "No se pudo obtener información del tenant o suscripción."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Acceder al esquema público para obtener el uso
        with schema_context("public"):
            uso, _ = UsoTenant.objects.get_or_create(tenant=tenant)
        
        data = {
            "suscripcion": SuscripcionSerializer(suscripcion).data,
            "uso": UsoTenantSerializer(uso).data,
            "limite_hoteles": suscripcion.plan.max_hoteles,
            "limite_usuarios": suscripcion.plan.max_usuarios,
            "puede_crear_hotel": uso.hoteles < suscripcion.plan.max_hoteles,
            "puede_crear_usuario": uso.usuarios < suscripcion.plan.max_usuarios,
        }
        
        serializer = EstadisticasUsoSerializer(data)
        return Response(serializer.data)

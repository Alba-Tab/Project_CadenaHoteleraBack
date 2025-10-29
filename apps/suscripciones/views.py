from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django_tenants.utils import schema_context
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from .models import Plan, Suscripcion, UsoTenant
from .serializers import (
    PlanSerializer, 
    SuscripcionSerializer, 
    UsoTenantSerializer,
    EstadisticasUsoSerializer,
    RenovarSuscripcionSerializer,
    PlanAgrupadoSerializer
)


class PlanPublicoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet público para consultar planes disponibles.
    NO requiere autenticación - accesible desde urls_public.py
    """
    queryset = Plan.objects.filter(activo=True)
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def agrupados(self, request):
        """
        Retorna planes agrupados por características similares.
        GET /api/planes/agrupados/
        
        Agrupa planes que tienen los mismos max_usuarios y max_hoteles,
        mostrando sus variantes de precio/tipo.
        """
        planes = Plan.objects.filter(activo=True).order_by('nombre', 'tipo')
        
        # Diccionario para agrupar: key=(nombre, max_usuarios, max_hoteles)
        grupos = defaultdict(list)
        
        for plan in planes:
            key = (plan.nombre, plan.max_usuarios, plan.max_hoteles)
            grupos[key].append({
                'id': plan.id,
                'precio': str(plan.precio),
                'tipo': plan.tipo,
                'tipo_display': plan.get_tipo_display()
            })
        
        # Convertir a lista de planes agrupados
        resultado = []
        for (nombre, max_usuarios, max_hoteles), variantes in grupos.items():
            resultado.append({
                'nombre': nombre,
                'max_usuarios': max_usuarios,
                'max_hoteles': max_hoteles,
                'variantes': variantes
            })
        
        # Ordenar por nombre
        resultado.sort(key=lambda x: x['nombre'])
        
        serializer = PlanAgrupadoSerializer(resultado, many=True)
        return Response(serializer.data)


class PlanAdminViewSet(viewsets.ModelViewSet):
    """
    ViewSet para administradores - CRUD completo de planes.
    Requiere autenticación y permisos de administrador.
    Accesible desde urls_public.py en /api/admin/planes/
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]  # Solo administradores
    
    def get_queryset(self):
        """Permite filtrar por activo si se especifica"""
        queryset = Plan.objects.all()
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        return queryset.order_by('nombre', 'tipo')


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
    
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def renovar(self, request):
        """
        Renueva la suscripción del tenant con un nuevo plan.
        POST /api/mi-suscripcion/renovar/
        Body: { "plan_id": 2 }
        """
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response(
                {"detail": "No se pudo identificar el tenant."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar datos de entrada
        serializer = RenovarSuscripcionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        nuevo_plan = serializer.validated_data['plan_id']
        
        # Obtener suscripción actual
        with schema_context("public"):
            suscripcion_actual = Suscripcion.objects.filter(
                tenant=tenant
            ).order_by('-fin_periodo').first()
            
            if not suscripcion_actual:
                return Response(
                    {"detail": "No existe una suscripción previa para este tenant."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calcular nuevas fechas
            # Si la suscripción actual aún está vigente, extender desde fin_periodo
            # Si ya venció, comenzar desde hoy
            hoy = timezone.now().date()
            if suscripcion_actual.fin_periodo >= hoy:
                inicio_periodo = suscripcion_actual.fin_periodo + timedelta(days=1)
            else:
                inicio_periodo = hoy
            
            # Calcular fin_periodo según el tipo del nuevo plan
            if nuevo_plan.tipo == "Mensual":
                fin_periodo = inicio_periodo + timedelta(days=30)
            elif nuevo_plan.tipo == "Anual":
                fin_periodo = inicio_periodo + timedelta(days=365)
            elif nuevo_plan.tipo == "Trimestral":  # Trimestral
                fin_periodo = inicio_periodo + timedelta(days=90)
            else:
                fin_periodo = inicio_periodo + timedelta(days=30)
            
            # Marcar suscripción actual como cancelada si está activa
            if suscripcion_actual.estado in ("activo", "prueba"):
                suscripcion_actual.estado = "cancelado"
                suscripcion_actual.save()
            
            # Crear nueva suscripción
            nueva_suscripcion = Suscripcion.objects.create(
                tenant=tenant,
                plan=nuevo_plan,
                estado="activo",
                inicio_periodo=inicio_periodo,
                fin_periodo=fin_periodo
            )
            
            # Actualizar contadores si el plan cambió los límites
            uso, _ = UsoTenant.objects.get_or_create(tenant=tenant)
            
            # Validar que los recursos actuales no excedan los nuevos límites
            if uso.hoteles > nuevo_plan.max_hoteles:
                return Response(
                    {
                        "detail": f"No puedes cambiar a este plan. Tienes {uso.hoteles} hoteles "
                                 f"y el nuevo plan solo permite {nuevo_plan.max_hoteles}. "
                                 f"Elimina hoteles antes de cambiar de plan."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if uso.usuarios > nuevo_plan.max_usuarios:
                return Response(
                    {
                        "detail": f"No puedes cambiar a este plan. Tienes {uso.usuarios} usuarios "
                                 f"y el nuevo plan solo permite {nuevo_plan.max_usuarios}. "
                                 f"Elimina usuarios antes de cambiar de plan."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            {
                "detail": "Suscripción renovada exitosamente.",
                "suscripcion": SuscripcionSerializer(nueva_suscripcion).data,
                "plan_anterior": suscripcion_actual.plan.nombre,
                "plan_nuevo": nuevo_plan.nombre,
                "nuevos_limites": {
                    "max_hoteles": nuevo_plan.max_hoteles,
                    "max_usuarios": nuevo_plan.max_usuarios
                }
            },
            status=status.HTTP_201_CREATED
        )

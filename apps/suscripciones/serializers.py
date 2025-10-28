from rest_framework import serializers
from .models import Plan, Suscripcion, UsoTenant


class PlanSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Plan."""
    
    class Meta:
        model = Plan
        fields = [
            'id',
            'nombre',
            'max_usuarios',
            'max_hoteles',
            'precio',
            'tipo',
            'activo'
        ]
        read_only_fields = ['id']


class SuscripcionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Suscripcion."""
    plan_nombre = serializers.CharField(source='plan.nombre', read_only=True)
    plan_detalles = PlanSerializer(source='plan', read_only=True)
    tenant_nombre = serializers.CharField(source='tenant.schema_name', read_only=True)
    esta_activa = serializers.SerializerMethodField()
    dias_restantes = serializers.SerializerMethodField()
    
    class Meta:
        model = Suscripcion
        fields = [
            'id',
            'tenant',
            'tenant_nombre',
            'plan',
            'plan_nombre',
            'plan_detalles',
            'estado',
            'inicio_periodo',
            'fin_periodo',
            'esta_activa',
            'dias_restantes'
        ]
        read_only_fields = ['id', 'tenant']
    
    def get_esta_activa(self, obj):
        """Indica si la suscripción está activa."""
        return obj.puede_escribir
    
    def get_dias_restantes(self, obj):
        """Calcula los días restantes de la suscripción."""
        from django.utils import timezone
        if obj.fin_periodo:
            delta = obj.fin_periodo - timezone.now().date()
            return max(0, delta.days)
        return 0


class UsoTenantSerializer(serializers.ModelSerializer):
    """Serializer para el modelo UsoTenant."""
    tenant_nombre = serializers.CharField(source='tenant.schema_name', read_only=True)
    porcentaje_hoteles = serializers.SerializerMethodField()
    porcentaje_usuarios = serializers.SerializerMethodField()
    
    class Meta:
        model = UsoTenant
        fields = [
            'id',
            'tenant',
            'tenant_nombre',
            'hoteles',
            'usuarios',
            'ultima_actualizacion',
            'porcentaje_hoteles',
            'porcentaje_usuarios'
        ]
        read_only_fields = ['id', 'tenant', 'ultima_actualizacion']
    
    def get_porcentaje_hoteles(self, obj):
        """Calcula el porcentaje de uso de hoteles."""
        suscripcion = obj.tenant.suscripciones.filter(estado__in=["activo", "prueba"]).first()
        if suscripcion and suscripcion.plan.max_hoteles > 0:
            return round((obj.hoteles / suscripcion.plan.max_hoteles) * 100, 2)
        return 0
    
    def get_porcentaje_usuarios(self, obj):
        """Calcula el porcentaje de uso de usuarios."""
        suscripcion = obj.tenant.suscripciones.filter(estado__in=["activo", "prueba"]).first()
        if suscripcion and suscripcion.plan.max_usuarios > 0:
            return round((obj.usuarios / suscripcion.plan.max_usuarios) * 100, 2)
        return 0


class EstadisticasUsoSerializer(serializers.Serializer):
    """Serializer para estadísticas de uso de un tenant."""
    suscripcion = SuscripcionSerializer(read_only=True)
    uso = UsoTenantSerializer(read_only=True)
    limite_hoteles = serializers.IntegerField(read_only=True)
    limite_usuarios = serializers.IntegerField(read_only=True)
    puede_crear_hotel = serializers.BooleanField(read_only=True)
    puede_crear_usuario = serializers.BooleanField(read_only=True)

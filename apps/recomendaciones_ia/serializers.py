from rest_framework import serializers
from .models import RecomendacionPrecio, HistorialRecomendacion
from apps.habitaciones.serializers import HabitacionSerializer


class RecomendacionPrecioSerializer(serializers.ModelSerializer):
    """
    Serializer para las recomendaciones de precios generadas por IA
    """
    habitacion_detalle = HabitacionSerializer(source='habitacion', read_only=True)
    cambio_absoluto = serializers.SerializerMethodField()
    cambio_porcentaje = serializers.SerializerMethodField()
    
    class Meta:
        model = RecomendacionPrecio
        fields = [
            'id',
            'habitacion',
            'habitacion_detalle',
            'tarifa_actual',
            'tarifa_sugerida',
            'cambio_absoluto',
            'cambio_porcentaje',
            'confianza',
            'motivo',
            'fecha_generacion',
            'aceptada',
            'aplicada'
        ]
        read_only_fields = ['fecha_generacion', 'aceptada', 'aplicada']
    
    def get_cambio_absoluto(self, obj):
        """Calcula el cambio absoluto en bolivianos"""
        return float(obj.tarifa_sugerida - obj.tarifa_actual)
    
    def get_cambio_porcentaje(self, obj):
        """Calcula el cambio porcentual"""
        if obj.tarifa_actual > 0:
            cambio = ((obj.tarifa_sugerida - obj.tarifa_actual) / obj.tarifa_actual) * 100
            return round(cambio, 2)
        return 0


class HistorialRecomendacionSerializer(serializers.ModelSerializer):
    """
    Serializer para el historial de recomendaciones aceptadas
    """
    habitacion_detalle = HabitacionSerializer(source='habitacion', read_only=True)
    aceptado_por_nombre = serializers.CharField(source='aceptado_por.get_full_name', read_only=True)
    cambio_porcentaje = serializers.ReadOnlyField()
    
    class Meta:
        model = HistorialRecomendacion
        fields = [
            'id',
            'habitacion',
            'habitacion_detalle',
            'tarifa_anterior',
            'tarifa_nueva',
            'cambio_porcentaje',
            'confianza',
            'motivo',
            'fecha_aceptacion',
            'aceptado_por',
            'aceptado_por_nombre'
        ]
        read_only_fields = ['fecha_aceptacion']


class AceptarRecomendacionSerializer(serializers.Serializer):
    """
    Serializer para aceptar recomendaciones (una o todas)
    """
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='Lista de IDs de recomendaciones a aceptar'
    )
    todas = serializers.BooleanField(
        required=False,
        default=False,
        help_text='Si es True, acepta todas las recomendaciones pendientes'
    )
    
    def validate(self, data):
        """Valida que se proporcione al menos uno de los campos"""
        if not data.get('ids') and not data.get('todas'):
            raise serializers.ValidationError(
                'Debes proporcionar una lista de IDs o marcar "todas" como True'
            )
        return data

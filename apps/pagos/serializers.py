from rest_framework import serializers
from .models import Pago
from apps.folioestancias.models import FolioEstancia


class PagoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Pago.
    Incluye validaciones y campos adicionales de solo lectura.
    """
    # Campos de solo lectura con información adicional
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Pago
        fields = [
            'id',
            'estado',
            'estado_display',
            'fecha_pago',
            'metodo',
            'monto',
            'referencia',
            'folio_estancia',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_monto(self, value):
        """
        Valida que el monto sea mayor a cero.
        """
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a cero.")
        return value
    
    def validate_folio_estancia(self, value):
        """
        Valida que el folio de estancia exista.
        """
        if value and not FolioEstancia.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("El folio de estancia no existe.")
        return value
    
    def validate(self, data):
        """
        Validaciones a nivel de objeto.
        """
        # Validar que la fecha de pago no sea futura
        from datetime import date
        if data.get('fecha_pago') and data['fecha_pago'] > date.today():
            raise serializers.ValidationError({
                'fecha_pago': 'La fecha de pago no puede ser futura.'
            })
        
        return data


class PagoDetalleSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para Pago con información del folio de estancia.
    """
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    folio_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Pago
        fields = [
            'id',
            'estado',
            'estado_display',
            'fecha_pago',
            'metodo',
            'monto',
            'referencia',
            'folio_estancia',
            'folio_info',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'folio_info']
    
    def get_folio_info(self, obj):
        """
        Retorna información básica del folio de estancia.
        """
        if obj.folio_estancia:
            return {
                'id': obj.folio_estancia.id,
                'estado': obj.folio_estancia.estado,
                'total_pagado': str(obj.folio_estancia.total_pagado),
            }
        return None

# apps/servicios_asociados/serializers.py
from rest_framework import serializers
from .models import ServiciosAsociados

class ServiciosAsociadosSerializer(serializers.ModelSerializer):
    nombre_servicio = serializers.ReadOnlyField(source='servicio.nombre')
    precio_unitario = serializers.ReadOnlyField(source='servicio.precio')  # ✅ Leer precio del servicio
   

    class Meta:
        model = ServiciosAsociados
        fields = [
            "id",
            "servicio",
            "reserva",
            "folioestancia",
            "cantidad",
            "monto_total",
            "fecha_servicio",
            "estado",          
            "observaciones",    
            "nombre_servicio",
            "precio_unitario",  
        ]
        read_only_fields = ['monto_total', 'fecha_servicio']

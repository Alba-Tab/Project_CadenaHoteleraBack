from rest_framework import serializers
from .models import ServiciosAsociados

class ServiciosAsociadosSerializer(serializers.ModelSerializer):
    nombre_servicio = serializers.ReadOnlyField(source='servicio.nombre')
    class Meta:
        model = ServiciosAsociados
        fields = ["id", "nombre_servicio", "cantidad", "monto_total"]
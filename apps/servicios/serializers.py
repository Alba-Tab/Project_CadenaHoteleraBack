from rest_framework import serializers
from .models import Servicio, ServicioReserva

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ["id", "nombre", "descripcion", "precio", "tipo", "created_at", "updated_at"]

class ServicioReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicioReserva
        fields = '__all__'
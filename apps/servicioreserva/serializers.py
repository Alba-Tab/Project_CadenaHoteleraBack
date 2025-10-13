from rest_framework import serializers
from .models import ServicioReserva


class ServicioReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicioReserva
        fields = '__all__'
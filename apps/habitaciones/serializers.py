from rest_framework import serializers
from .models import Habitacion

class HabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habitacion
        fields = '__all__'

class HabitacionSimpleSerializer(serializers.ModelSerializer):
    nombre_hotel = serializers.CharField(
        source='hotel.nombre',
        read_only=True
    )

    class Meta:
        model = Habitacion
        fields = ['id', 'numero', 'tipo', 'precio_noche', 'nombre_hotel']
from rest_framework import serializers
from .models import Habitacion

class HabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habitacion
        fields = '__all__'

class HabitacionRankingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    numero = serializers.CharField(max_length=10)
    tipo = serializers.CharField(max_length=50)
    precio_noche = serializers.DecimalField(max_digits=10, decimal_places=2)
    hotel__nombre = serializers.CharField(max_length=100)
    total_reservas = serializers.IntegerField()
from rest_framework import serializers


class HabitacionRecomendacionSerializer(serializers.Serializer):
    habitacion_id = serializers.IntegerField()
    hotel_id = serializers.IntegerField()
    hotel_nombre = serializers.CharField()
    numero = serializers.CharField()
    tipo = serializers.CharField()
    precio_noche = serializers.DecimalField(max_digits=10, decimal_places=2)
    reservas_totales = serializers.IntegerField()
    noches_reservadas = serializers.IntegerField()
    porcentaje_ocupacion = serializers.FloatField()
    ranking = serializers.IntegerField()
    recomendacion_porcentaje = serializers.FloatField()
    precio_recomendado = serializers.DecimalField(max_digits=10, decimal_places=2)
    motivo = serializers.CharField()


class RecomendacionesHabitacionesResponseSerializer(serializers.Serializer):
    fecha_inicio = serializers.CharField(allow_null=True)
    fecha_fin = serializers.CharField(allow_null=True)
    dias_periodo = serializers.IntegerField()
    habitaciones = HabitacionRecomendacionSerializer(many=True)

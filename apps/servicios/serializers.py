from os import read
from rest_framework import serializers
from .models import Servicio

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ["id", "nombre", "descripcion", "precio", "tipo", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

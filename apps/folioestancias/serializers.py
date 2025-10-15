from rest_framework import serializers

from apps.folioestancias.models import FolioEstancia


class FolioEstanciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolioEstancia
        fields = '__all__'
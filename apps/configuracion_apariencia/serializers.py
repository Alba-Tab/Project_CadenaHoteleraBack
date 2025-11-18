from rest_framework import serializers

from .models import ConfiguracionApariencia




class ConfiguracionAparienciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionApariencia
        fields = [
            'id', 'hotel', 'color_primario', 'color_secundario',
            'color_fondo', 'familia_fuente', 'tamano_fuente_base',
            'modo_tema', 'logo_key', 'tema', 'tipo_letra',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['id', 'hotel', 'creado_en', 'actualizado_en']

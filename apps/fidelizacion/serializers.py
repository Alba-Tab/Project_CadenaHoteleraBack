from rest_framework import serializers
from .models import ProgramaFidelizacion, CuentaFidelizacion
from apps.usuarios.serializers import UserSerializer


class ProgramaFidelizacionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo ProgramaFidelizacion"""
    
    class Meta:
        model = ProgramaFidelizacion
        fields = [
            'id', 
            'nombre', 
            'descripcion', 
            'descuento_maximo', 
            'activo', 
            'puntos_por_dolar_descuento'
        ]
        read_only_fields = ['id']

    def validate_descuento_maximo(self, value):
        if value < 1 or value > 100:
            raise serializers.ValidationError(
                "El descuento máximo debe estar entre 1% y 100%"
            )
        return value

    def validate_puntos_por_dolar_descuento(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Los puntos por dólar de descuento deben ser mayor a 0"
            )
        return value


class CuentaFidelizacionSerializer(serializers.ModelSerializer):
    
    cliente_info = UserSerializer(source='cliente', read_only=True)
    programa_info = ProgramaFidelizacionSerializer(source='fidelizacion', read_only=True)
    descuento_disponible = serializers.SerializerMethodField()
    
    class Meta:
        model = CuentaFidelizacion
        fields = [
            'id',
            'cliente',
            'cliente_info',
            'fidelizacion',
            'programa_info',
            'puntos_acumulados',
            'descuento_disponible'
        ]
        read_only_fields = ['id', 'puntos_acumulados']

    def get_descuento_disponible(self, obj):
        """Calcula el descuento disponible basado en un monto de ejemplo de $100"""
        if obj.fidelizacion and obj.fidelizacion.activo:
            return obj.calcular_descuento_disponible(100)  # Monto de ejemplo
        return 0


class CuentaFidelizacionCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CuentaFidelizacion
        fields = ['cliente', 'fidelizacion']

    def validate(self, data):
        cliente = data.get('cliente')
        programa = data.get('fidelizacion')
        
        if CuentaFidelizacion.objects.filter(
            cliente=cliente, fidelizacion=programa
        ).exists():
            raise serializers.ValidationError(
                "El cliente ya tiene una cuenta en este programa de fidelización"
            )
        
        if not programa.activo:
            raise serializers.ValidationError(
                "No se puede crear una cuenta en un programa inactivo"
            )
        
        return data


class AcumularPuntosSerializer(serializers.Serializer):
    monto_gastado = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_monto_gastado(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El monto gastado debe ser mayor a 0"
            )
        return value


class CanjearPuntosSerializer(serializers.Serializer):
    monto_descuento = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_cuenta = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_monto_descuento(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El monto de descuento debe ser mayor a 0"
            )
        return value
    
    def validate_total_cuenta(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El total de la cuenta debe ser mayor a 0"
            )
        return value

    def validate(self, data):
        monto_descuento = data.get('monto_descuento')
        total_cuenta = data.get('total_cuenta')
        
        if monto_descuento > total_cuenta:
            raise serializers.ValidationError(
                "El descuento no puede ser mayor al total de la cuenta"
            )
        
        return data
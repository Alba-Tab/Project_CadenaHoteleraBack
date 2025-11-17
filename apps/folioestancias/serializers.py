from rest_framework import serializers
from apps.folioestancias.models import FolioEstancia
from apps.servicios_asociados.models import ServiciosAsociados
from apps.servicios_asociados.serializers import ServiciosAsociadosSerializer
from decimal import Decimal 

class FolioEstanciaSerializer(serializers.ModelSerializer):
    # Campos calculados
    huesped_nombre = serializers.CharField(
        source='huesped.get_full_name', read_only=True
    )
    reserva_id = serializers.IntegerField(source='reserva.id', read_only=True)
    reserva_total = serializers.DecimalField(
        source='reserva.total', max_digits=10, decimal_places=2, read_only=True
    )
    fecha_entrada = serializers.DateField(source='reserva.fecha_entrada', read_only=True)
    fecha_salida = serializers.DateField(source='reserva.fecha_salida', read_only=True)
    hotel_nombre = serializers.CharField(source='reserva.hotel.nombre', read_only=True)
    total_pagado = serializers.SerializerMethodField()

    class Meta:
        model = FolioEstancia
        fields = [
            "id",
            "estado",
            "total_pagado",
            "huesped_id",
            "huesped_nombre",
            "reserva_id",
            "reserva_total",
            "fecha_entrada",
            "fecha_salida",
            "hotel_nombre",
        ]
    
    def get_total_pagado(self, obj):
        """Total a pagar (reserva + servicios asociados)"""
        return str(obj.calcular_total_general())


# --- SERIALIZER DETALLE ---
class FolioDetalleSerializer(serializers.ModelSerializer):
    huesped_nombre = serializers.CharField(source='huesped.get_full_name', read_only=True)
    hotel_nombre = serializers.CharField(source='reserva.hotel.nombre', read_only=True)
    reserva_total = serializers.DecimalField(source='reserva.total', max_digits=10, decimal_places=2, read_only=True)
    fecha_entrada = serializers.DateField(source='reserva.fecha_entrada', read_only=True)
    fecha_salida = serializers.DateField(source='reserva.fecha_salida', read_only=True)

    # servicios asociados a la reserva
    servicios_reservas = ServiciosAsociadosSerializer(
        many=True,
        read_only=True,
        source='reserva.servicios_reserva'  # <- debe coincidir con el related_name del modelo
    )

    class Meta:
        model = FolioEstancia
        fields = [
            "id",
            "estado",
            "total_pagado",
            "huesped_id",
            "huesped_nombre",
            "reserva_id",
            "reserva_total",
            "fecha_entrada",
            "fecha_salida",
            "hotel_nombre",
            "servicios_reservas",
        ]


class FolioDetalleCompletoSerializer(serializers.ModelSerializer):
    """Serializer que retorna el desglose completo del folio con todos los conceptos"""
    
    huesped_nombre = serializers.CharField(source='huesped.get_full_name', read_only=True)
    hotel_nombre = serializers.CharField(source='reserva.hotel.nombre', read_only=True)
    fecha_entrada = serializers.DateField(source='reserva.fecha_entrada', read_only=True)
    fecha_salida = serializers.DateField(source='reserva.fecha_salida', read_only=True)
    
    # Campos calculados
    conceptos = serializers.SerializerMethodField()
    total_general = serializers.SerializerMethodField()
    
    class Meta:
        model = FolioEstancia
        fields = [
            "id",
            "estado",
            "huesped_id",
            "huesped_nombre",
            "hotel_nombre",
            "fecha_entrada",
            "fecha_salida",
            "conceptos",
            "total_general",
        ]
    
    def get_conceptos(self, obj):
        """Retorna la lista de todos los conceptos del folio"""
        conceptos = []
        
        # 1. Concepto de Reserva (siempre cantidad = 1)
        conceptos.append({
            "concepto": "Reserva de Habitación",
            "descripcion": f"Habitación {obj.reserva.habitacion.numero} - {obj.reserva.habitacion.tipo}",
            "cantidad": 1,
            "precio_unitario": str(obj.reserva.total),
            "subtotal": str(obj.reserva.total)
        })
        
        # 2. Servicios Asociados al Folio
        servicios = ServiciosAsociados.objects.filter(folioestancia=obj)
        for servicio in servicios:
            conceptos.append({
                "concepto": servicio.servicio.nombre,
                "descripcion": servicio.observaciones or servicio.servicio.descripcion,
                "cantidad": servicio.cantidad,
                "precio_unitario": str(servicio.servicio.precio),
                "subtotal": str(servicio.monto_total)
            })
        
        return conceptos
    
    def get_total_general(self, obj):
        """Total general del folio (reserva + servicios)"""
        return str(obj.calcular_total_general())

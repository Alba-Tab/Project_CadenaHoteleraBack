from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.folioestancias.models import FolioEstancia
from apps.folioestancias.serializers import (
    FolioEstanciaSerializer, 
    FolioDetalleSerializer,
    FolioDetalleCompletoSerializer
)
from rest_framework.response import Response
from rest_framework.decorators import action


class FolioEstanciaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        FolioEstancia.objects
        .select_related('reserva', 'huesped', 'reserva__hotel')
        .order_by('-id')
    )
    serializer_class = FolioEstanciaSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='huesped/(?P<huesped_id>[^/.]+)')
    def folios_por_huesped(self, request, huesped_id=None):
        folios = self.queryset.filter(huesped_id=huesped_id)
        serializer = self.get_serializer(folios, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='detalle-completo')
    def detalle_completo(self, request, pk=None):
        """
        Retorna el detalle completo del folio con el desglose de todos los conceptos:
        - Reserva (cantidad: 1)
        - Servicios asociados (cantidad: N)
        - Totales y saldo pendiente
        
        GET /api/folioestancias/{id}/detalle-completo/
        """
        folio = self.get_object()
        serializer = FolioDetalleCompletoSerializer(folio)
        return Response(serializer.data, status=status.HTTP_200_OK)

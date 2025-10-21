from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.folioestancias.models import FolioEstancia
from apps.folioestancias.serializers import FolioEstanciaSerializer, FolioDetalleSerializer
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
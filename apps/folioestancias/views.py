from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.folioestancias.models import FolioEstancia
from apps.folioestancias.serializers import FolioEstanciaSerializer, DetalleFolioSerializer


class FolioEstanciaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FolioEstancia.objects.all().order_by('-id')
    serializer_class = FolioEstanciaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtrar folios por pendientes
        return self.queryset.filter(estado=FolioEstancia.PENDIENTE)

    @action(
        detail=True,
        methods=['get'],
        url_path='detalle-folio',
        serializer_class=DetalleFolioSerializer
    )
    def detalle_folio(self, request, pk=None):
        # Obtener el folio de estancia específico
        folio = self.get_object()
        # Serializar y devolver los detalles del folio
        serializer = DetalleFolioSerializer(folio)
        return Response(serializer.data)
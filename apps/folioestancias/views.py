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

    @action(
        detail=True,
        methods=['get'],
        url_path='detalle-folio',
        serializer_class=FolioDetalleSerializer
    )
    def detalle_folio(self, request, pk=None):
        # Obtener el folio de estancia específico
        folio = self.get_object()
        # Serializar y devolver los detalles del folio
        serializer = FolioDetalleSerializer(folio)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        url_path='folios-pendientes',
        serializer_class=FolioEstanciaSerializer
    )
    def folios_pendientes(self, request):
        """Devuelve todos los folios en estado PENDIENTE, ordenados por -id."""
        folios = FolioEstancia.objects.filter(estado=FolioEstancia.PENDIENTE).order_by('-id')
        serializer = FolioEstanciaSerializer(folios, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        url_path='pendientes-por-usuario',
        serializer_class=FolioEstanciaSerializer
    )
    def pendientes_por_usuario(self, request):
        """Devuelve los folios de un usuario indicado por ?id_usuario=<id>.

        Si no se proporciona id_usuario o no es válido, devuelve 400.
        Devuelve todos los folios del usuario (independientemente de estado), ordenados por -id.
        """
        id_usuario = request.query_params.get('id_usuario')
        if not id_usuario:
            return Response({'detail': 'Falta parámetro id_usuario'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            usuario_id = int(id_usuario)
        except (TypeError, ValueError):
            return Response({'detail': 'id_usuario debe ser un entero'}, status=status.HTTP_400_BAD_REQUEST)

        folios = FolioEstancia.objects.filter(huesped_id=usuario_id, estado=FolioEstancia.PENDIENTE).order_by('-id')
        serializer = FolioEstanciaSerializer(folios, many=True)
        return Response(serializer.data)

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

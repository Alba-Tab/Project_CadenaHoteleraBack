from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

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

    @action(
        detail=False,
        methods=['get'],
        url_path='por-usuario',
        serializer_class=FolioEstanciaSerializer
    )
    def por_usuario(self, request):
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

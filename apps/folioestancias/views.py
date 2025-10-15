from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.folioestancias.models import FolioEstancia
from apps.folioestancias.serializers import FolioEstanciaSerializer, DetalleFolioSerializer


# Create your views here.
class FolioEstanciaViewSet(viewsets.ModelViewSet):
    queryset = FolioEstancia.objects.all()
    serializer_class = FolioEstanciaSerializer

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_staff:
    #         return FolioEstancia.objects.all()
    #     return FolioEstancia.objects.filter(huesped=user)

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
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.folioestancias.models import FolioEstancia
from apps.folioestancias.serializers import FolioEstanciaSerializer


class FolioEstanciaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FolioEstancia.objects.all().order_by('-id')
    serializer_class = FolioEstanciaSerializer
    permission_classes = [IsAuthenticated]

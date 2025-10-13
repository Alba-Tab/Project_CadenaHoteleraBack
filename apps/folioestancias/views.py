from django.shortcuts import render
from rest_framework import viewsets

from apps.folioestancias.models import FolioEstancia
from apps.folioestancias.serializers import FolioEstanciaSerializer


# Create your views here.
class FolioEstanciaViewSet(viewsets.ModelViewSet):
    queryset = FolioEstancia.objects.all()
    serializer_class = FolioEstanciaSerializer

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_staff:
    #         return FolioEstancia.objects.all()
    #     return FolioEstancia.objects.filter(huesped=user)
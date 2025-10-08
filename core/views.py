from rest_framework import serializers, viewsets
from core.models import Tenant, Domain
from core.serializers import TenantSerializer


class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

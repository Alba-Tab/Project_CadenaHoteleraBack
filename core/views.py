from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from core.models import Tenant
from rest_framework.response import Response
from core.serializers import TenantSerializer
from core.services import TenantService


class TenantViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = TenantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = TenantService.create_tenant_with_domain(serializer.validated_data) #type:ignore
        except Exception as exc:
            return Response(
                {"detail": "No se pudo crear el tenant", "error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = {**result}
        schema = serializer.validated_data["schema_name"] #type:ignore
        domain = serializer.validated_data["domain"] #type:ignore
        if schema:
            payload["schema_name"] = schema
        if domain:
            payload["domain"] = domain
        return Response(payload, status=status.HTTP_201_CREATED)
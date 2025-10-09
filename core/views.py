from rest_framework import viewsets, status, mixins
from rest_framework.permissions import AllowAny
from core.models import Tenant
from rest_framework.response import Response
from core.serializers import TenantFormSerializer, TenantModelSerializer
from core.services import TenantFormService
from rest_framework.views import APIView

class TenantViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Tenant.objects.all() 
    serializer_class = TenantModelSerializer
    def create(self, request, *args, **kwargs):
        """Crear tenant + domain"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        schema_name = serializer.validated_data["schema_name"]
        name = serializer.validated_data["name"]
        domain = serializer.validated_data["domain"]

        try:
            result = TenantFormService.create_tenant_basic(
                schema_name=schema_name,
                name=name,
                domain=domain
            )
        except Exception as exc:
            return Response(
                {"detail": "No se pudo crear el tenant", "error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(result, status=status.HTTP_201_CREATED)
 
class TenantFormViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = TenantFormSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = TenantFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = TenantFormService.create_tenant_with_domain(serializer.validated_data) #type:ignore
        except Exception as exc:
            return Response(
                {"detail": "No se pudo crear el tenant", "error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(result, status=status.HTTP_201_CREATED)

class PublicSchemaView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        from django_tenants.utils import get_tenant_model
        TenantModel = get_tenant_model()

        if TenantModel.objects.filter(schema_name="public").exists():
            return Response({"detail": "El esquema público ya existe"}, status=200)

        public_tenant = TenantModel(schema_name="public", name="Public Schema")
        public_tenant.save()

        return Response({"detail": "Esquema público creado"}, status=201)
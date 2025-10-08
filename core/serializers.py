from rest_framework import serializers
from core.models import Tenant, Domain

class TenantSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(write_only=True)

    class Meta:
        model = Tenant
        fields = ["name", "schema_name", "domain"]

    def create(self, validated_data):
        domain_name = validated_data.pop("domain")
        tenant = Tenant(**validated_data)
        tenant.save()  # crea el schema físico y migra
        Domain.objects.create(domain=domain_name, tenant=tenant, is_primary=True)
        return tenant

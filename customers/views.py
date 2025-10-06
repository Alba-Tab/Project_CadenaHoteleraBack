from rest_framework import serializers, viewsets
from customers.models import Client, Domain

class ClientSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(write_only=True)

    class Meta:
        model = Client
        fields = ["name", "schema_name", "domain"]

    def create(self, validated_data):
        domain_name = validated_data.pop("domain")
        client = Client(**validated_data)
        client.save()  # crea el schema físico y migra
        Domain.objects.create(domain=domain_name, tenant=client, is_primary=True)
        return client


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

from django.conf import settings
from django.utils.text import slugify
from rest_framework import serializers
from core.models import Tenant, Domain
import re

DEFAULT_BASE_DOMAIN = getattr(settings, "TENANT_BASE_DOMAIN", "hotelapp.localhost")
class TenantSerializer(serializers.ModelSerializer):
    # Datos del formulario público
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    nombre_del_hotel = serializers.CharField(max_length=150)
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    #permitir sugerir subdominioy si no llega lo derivamos del nombre_del_hotel
    subdominio = serializers.CharField(write_only=True, required=False, allow_blank=True)

    # Campos calculados solo lectura para la respuesta
    domain = serializers.CharField(read_only=True)
    schema_name = serializers.CharField(read_only=True)

    class Meta:
        model = Tenant
        fields = [
            "first_name", "last_name", "email", "phone",
            "nombre_del_hotel", "username", "password",
            "subdominio","domain", "schema_name"
        ]

    def validate(self, attrs):
        # Normalizar subdominio 
        base = attrs.get("subdominio") or attrs["nombre_del_hotel"]
        candidate = slugify(base, allow_unicode=False)
        sub = re.sub(r'[^a-z]', '', candidate.lower())[:63]
        if not sub:
            raise serializers.ValidationError({"subdominio": "No se pudo generar un subdominio válido."})
        if sub == "public":
            raise serializers.ValidationError({"subdominio": "El subdominio 'public' está reservado."})

        base_domain = DEFAULT_BASE_DOMAIN
        full_domain = f"{sub}.{base_domain}"

        if Domain.objects.filter(domain=full_domain).exists():
            raise serializers.ValidationError({"subdominio": "El dominio ya existe. Elige otro subdominio."})

        if ":" in full_domain or full_domain.startswith("www."):
            raise serializers.ValidationError({"subdominio": "No incluir puerto ni 'www' en el dominio."})

        attrs["schema_name"] = sub
        attrs["domain"] = full_domain
        return attrs

from django.conf import settings
from django.utils.text import slugify
from rest_framework import serializers
from core.models import Tenant
import re
from apps.suscripciones.models import Plan


class TenantModelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tenant
        fields = "__all__"
    
    def validate(self, attrs):
        base = attrs.get("schema_name") or attrs["name"]
        candidate = slugify(base, allow_unicode=False)
        sub = re.sub(r'[^a-z0-9_]', '', candidate.lower())[:63]
        
        if not sub:
            raise serializers.ValidationError({"schema_name": "No se pudo generar un código válido."})
        if sub == "public":
            raise serializers.ValidationError({"schema_name": "El código 'public' está reservado."})

        # Verificar que el schema_name no exista
        if Tenant.objects.filter(schema_name=sub).exists():
            raise serializers.ValidationError({"schema_name": "Este código ya existe. Elige otro."})

        attrs["schema_name"] = sub
        return attrs
    
    
class TenantFormSerializer(serializers.ModelSerializer):
    """
    Serializer para registro público de nuevos tenants.
    Ahora sin dominios - solo usa schema_name como identificador único.
    """
    # Datos del formulario público
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    nombre_empresa = serializers.CharField(max_length=150)
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    # Código de empresa (reemplaza subdominio)
    codigo_empresa = serializers.CharField(write_only=True, required=False, allow_blank=True)

    # Campos calculados solo lectura para la respuesta
    schema_name = serializers.CharField(read_only=True)

    # Campos para suscripción
    plan_id = serializers.IntegerField()
    
    class Meta:
        model = Tenant
        fields = [
            "first_name", "last_name", "email",
            "nombre_empresa", "username", "password", "phone",
            "codigo_empresa", "schema_name", "plan_id"
        ]

    def validate(self, attrs):
        # Validar que el plan existe y está activo
        plan_id = attrs.get("plan_id")
        if not plan_id:
            raise serializers.ValidationError({"plan_id": "El plan es requerido."})
        
        try:
            plan = Plan.objects.get(id=plan_id, activo=True)
            attrs["plan"] = plan  # Guardamos el objeto plan completo
        except Plan.DoesNotExist:
            raise serializers.ValidationError({"plan_id": "El plan seleccionado no existe o no está activo."})
        
        # Normalizar código de empresa (schema_name)
        base = attrs.get("codigo_empresa") or attrs["nombre_empresa"]
        candidate = slugify(base, allow_unicode=False)
        # Permitir letras, números, guiones y underscores
        sub = re.sub(r'[^a-z0-9_-]', '', candidate.lower())[:63]
        
        if not sub:
            raise serializers.ValidationError({"codigo_empresa": "No se pudo generar un código válido."})
        if sub == "public":
            raise serializers.ValidationError({"codigo_empresa": "El código 'public' está reservado."})

        # Verificar que el schema_name no exista
        if Tenant.objects.filter(schema_name=sub).exists():
            raise serializers.ValidationError({"codigo_empresa": "Este código ya existe. Elige otro."})

        attrs["schema_name"] = sub
        return attrs

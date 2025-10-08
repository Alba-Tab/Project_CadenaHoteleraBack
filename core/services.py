from typing import Dict, Any
from django.db import transaction
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from core.models import Tenant, Domain
from apps.hoteles.models import Hotel
class TenantService:
    @staticmethod
    @transaction.atomic
    def create_tenant_with_domain(validated: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea Tenant Domain esquema datos base y usuario admin del hotel.
        si falla algo, rollback automático.
        """
        nombre = validated["first_name"]
        apellido = validated["last_name"]
        email = validated["email"]
        telefono = validated.get("phone", 000000000)
        nombre_hotel = validated["nombre_del_hotel"]
        username = validated["username"]
        password = validated["password"]
        schema_name = validated["schema_name"]
        full_domain = validated["domain"]

        if Domain.objects.filter(domain=full_domain).exists():
            raise ValueError("Dominio ya existente.")

        tenant = Tenant(schema_name=schema_name, name=nombre_hotel) 
        tenant.save()

        Domain.objects.create(domain=full_domain, tenant=tenant, is_primary=True)

        # Crear datos del usuario
        User = get_user_model()
        with schema_context(tenant.schema_name):
            
            admin_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=nombre,
                last_name=apellido,
                #phone=telefono,
                is_staff=True,
            )
            Hotel_principal = Hotel.objects.create(
                nombre=nombre_hotel,
                direccion="Dirección por defecto",
                telefono=telefono,
                categoria=3,  # Por defecto 3 estrellas
            )
        return {
            "tenant_id": tenant.id, #type:ignore
            "schema_name": tenant.schema_name,
            "domain": full_domain,
            "admin_username": username,
            "admin_email": email,
            
        }
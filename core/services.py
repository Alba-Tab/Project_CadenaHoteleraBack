from typing import Dict, Any
from django.db import transaction
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from core.models import Tenant, Domain
from django.core.mail import send_mail
from config.settings import DEFAULT_FROM_EMAIL
class TenantFormService:
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
        nombre_empresa = validated["nombre_empresa"]
        username = validated["username"]
        password = validated["password"]
        schema_name = validated["schema_name"]
        full_domain = validated["domain"]

        if Domain.objects.filter(domain=full_domain).exists():
            raise ValueError("Dominio ya existente.")

        tenant = Tenant(schema_name=schema_name, name=nombre_empresa) 
        tenant.save()

        Domain.objects.create(domain=full_domain, tenant=tenant, is_primary=True)

        # Crear datos del usuario
        User = get_user_model()
        with schema_context(tenant.schema_name):
            
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=nombre,
                last_name=apellido,
                is_staff=True,
            )
            # Enviar correo de confirmación
        subject = "Tenant creado exitosamente"
        message = f"""
        Hola {username},

        Se ha creado tu tenant {tenant.name}.
        Accede en: https://{full_domain}
        tus credenciales son las siguientes:
        Usuario: {username}
        Contraseña: {password}
        Por favor, cambia tu contraseña después del primer inicio de sesión.
        
        Saludos,
        Equipo de soporte
        """
        send_mail(subject, message, DEFAULT_FROM_EMAIL, [email]) #type:ignore
        return {
            "tenant_id": tenant.id, #type:ignore
            "schema_name": tenant.schema_name,
            "domain": full_domain,
            "admin_username": username,
            "admin_email": email,
            
        }
    
    @staticmethod
    @transaction.atomic
    def create_tenant_basic(schema_name: str, name: str, domain: str) -> Dict[str, Any]:
        """
        Crea tenant + domain SIN usuario (uso interno/admin).
        Requiere: schema_name, name (nombre del tenant), domain.
        """
        if Domain.objects.filter(domain=domain).exists():
            raise ValueError("Dominio ya existente.")

        tenant = Tenant(schema_name=schema_name, name=name)
        tenant.save()

        Domain.objects.create(domain=domain, tenant=tenant, is_primary=True)

        return {
            "tenant_id": tenant.id,#type:ignore
            "schema_name": tenant.schema_name,
            "domain": domain,
        }

    @staticmethod
    def ensure_public_tenant(domain: str = "localhost") -> Dict[str, Any]:
        """
        Asegura que existe el tenant público (schema_name='public').
        Si ya existe, devuelve la info; si no, lo crea.
        No requiere parámetros (usa valores por defecto).
        ADVERTENCIA: Llamar antes de crear otros tenants (en migrate o startup, no en peticiones HTTP).
        """
        public_tenant = Tenant.objects.filter(schema_name="public").first()
        if public_tenant:
            public_domain = Domain.objects.filter(tenant=public_tenant, is_primary=True).first()
            return {
                "tenant_id": public_tenant.id,#type:ignore
                "schema_name": public_tenant.schema_name,
                "domain": public_domain.domain if public_domain else None,
                "created": False,
            }

        # Crear tenant público
        with transaction.atomic():
            public_tenant = Tenant(schema_name="public", name="Public")
            public_tenant.save()
            Domain.objects.create(domain=domain, tenant=public_tenant, is_primary=True)

        return {
            "tenant_id": public_tenant.id,#type:ignore
            "schema_name": public_tenant.schema_name,
            "domain": domain,
            "created": True,
        }
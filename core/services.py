from typing import Dict, Any
from django.db import transaction
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from core.models import Tenant, Domain
from django.core.mail import send_mail
from config.settings import DEFAULT_FROM_EMAIL
from datetime import timedelta
from django.utils import timezone
from apps.suscripciones.models import Suscripcion, UsoTenant
class TenantFormService:
    @staticmethod
    @transaction.atomic
    def create_tenant_with_domain(validated: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea Tenant Domain esquema datos base y usuario admin del hotel.
        Incluye creación de suscripción inicial basada en el plan seleccionado.
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
        plan = validated["plan"]

        if Domain.objects.filter(domain=full_domain).exists():
            raise ValueError("Dominio ya existente.")

        tenant = Tenant(schema_name=schema_name, name=nombre_empresa)
        tenant.save()
        print("TENANT CREADO")
        Domain.objects.create(domain=full_domain, tenant=tenant, is_primary=True)
        print("DOMINIO CREADO")
        
        # Calcular fechas de suscripción según el tipo de plan
        inicio_periodo = timezone.now().date()
        if plan.tipo == "Mensual":
            fin_periodo = inicio_periodo + timedelta(days=30)
        elif plan.tipo == "Anual":
            fin_periodo = inicio_periodo + timedelta(days=365)
        elif plan.tipo == "Trimestral":  # Trimestral
            fin_periodo = inicio_periodo + timedelta(days=90)
        else:
            fin_periodo = inicio_periodo + timedelta(days=30)  # Default mensual
        
        # Crear suscripción en esquema público
        suscripcion = Suscripcion.objects.create(
            tenant=tenant,
            plan=plan,
            estado="activo",
            inicio_periodo=inicio_periodo,
            fin_periodo=fin_periodo
        )
        print(f"SUSCRIPCIÓN CREADA: {plan.nombre}")
        
        # Crear registro de uso del tenant
        UsoTenant.objects.create(tenant=tenant)
        print("REGISTRO DE USO CREADO")
        
        # Crear usuario admin en el esquema del tenant
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
        
        # Enviar correo de confirmación con detalles del plan
        subject = "¡Bienvenido! Tu cuenta ha sido creada exitosamente"
        message = f"""
        Hola {nombre} {apellido},

        ¡Bienvenido a {nombre_empresa}!

        Tu cuenta ha sido creada exitosamente con los siguientes detalles:

        ═══════════════════════════════════════
        INFORMACIÓN DE ACCESO
        ═══════════════════════════════════════
        🌐 URL de acceso: http://{full_domain}/authentication/login
        👤 Usuario: {username}
        📧 Email: {email}

        ═══════════════════════════════════════
        DETALLES DE TU SUSCRIPCIÓN
        ═══════════════════════════════════════
        📦 Plan: {plan.nombre}
        💰 Precio: ${plan.precio:.2f}
        📅 Tipo: {plan.get_tipo_display()}
        📆 Fecha de inicio: {inicio_periodo.strftime('%d/%m/%Y')}
        📆 Fecha de vencimiento: {fin_periodo.strftime('%d/%m/%Y')}
        ✅ Estado: Activo

        ═══════════════════════════════════════
        LÍMITES DE TU PLAN
        ═══════════════════════════════════════
        🏨 Hoteles: {plan.max_hoteles}
        👥 Usuarios: {plan.max_usuarios}

        Puedes comenzar a crear tus hoteles y gestionar tu cadena hotelera.

        Si tienes alguna pregunta, no dudes en contactarnos.

        ¡Que tengas un excelente día!

        Saludos,
        Equipo de Soporte
        """
        print("ENVIANDO EMAIL")
        send_mail(subject, message, DEFAULT_FROM_EMAIL, [email]) #type:ignore
        print("EMAIL ENVIADO")

        return {
            "tenant_id": tenant.id, #type:ignore
            "schema_name": tenant.schema_name,
            "domain": full_domain,
            "admin_username": username,
            "admin_email": email,
            "message":message,
            "suscripcion": {
                "plan_nombre": plan.nombre,
                "plan_tipo": plan.get_tipo_display(),
                "precio": plan.precio,
                "inicio_periodo": inicio_periodo.isoformat(),
                "fin_periodo": fin_periodo.isoformat(),
                "estado": "activo",
                "max_hoteles": plan.max_hoteles,
                "max_usuarios": plan.max_usuarios,
            }
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

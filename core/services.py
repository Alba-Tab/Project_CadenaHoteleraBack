from typing import Dict, Any
from django.db import transaction, connection
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from core.models import Tenant, Domain
from django.core.mail import send_mail
from config.settings import DEFAULT_FROM_EMAIL
from datetime import timedelta
from django.utils import timezone
from apps.suscripciones.models import Suscripcion, UsoTenant
import threading
import logging
import time

logger = logging.getLogger(__name__)

class TenantFormService:
    @staticmethod
    def _process_tenant_background(tenant_id: int, validated: Dict[str, Any]):
        """
        Procesa las migraciones y configuración del tenant en segundo plano.
        Este método se ejecuta en un thread separado.
        """
        try:
            start_time = time.time()
            logger.info("=" * 60)
            logger.info("🔄 PROCESAMIENTO EN BACKGROUND INICIADO")
            logger.info("=" * 60)
            
            # Obtener el tenant creado
            tenant = Tenant.objects.get(id=tenant_id)
            schema_name = tenant.schema_name
            nombre = validated["first_name"]
            apellido = validated["last_name"]
            email = validated["email"]
            username = validated["username"]
            password = validated["password"]
            full_domain = validated["domain"]
            plan = validated["plan"]
            nombre_empresa = validated["nombre_empresa"]
            
            # 1. Crear el schema manualmente y ejecutar migraciones
            step_start = time.time()
            logger.info(f"🔵 Creando schema y ejecutando migraciones para '{schema_name}'...")
            
            from django.core.management import call_command
            from django.db import connection
            
            # Crear el schema manualmente
            with connection.cursor() as cursor:
                cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
            
            # Ejecutar migraciones en el nuevo schema
            call_command('migrate_schemas', '--schema', schema_name, verbosity=0)
            
            migration_time = time.time() - step_start
            logger.info(f"✅ Schema y migraciones completados: {migration_time:.2f}s")
            
            # 2. Crear usuario admin en el esquema del tenant
            step_start = time.time()
            logger.info(f"🔵 Creando usuario administrador...")
            User = get_user_model()
            with schema_context(schema_name):
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=nombre,
                    last_name=apellido,
                    is_staff=True,
                )
            user_time = time.time() - step_start
            logger.info(f"✅ Usuario admin creado: {user_time:.2f}s")
            
            # 3. Calcular fechas de suscripción
            inicio_periodo = timezone.now().date()
            if plan.tipo == "Mensual":
                fin_periodo = inicio_periodo + timedelta(days=30)
            elif plan.tipo == "Anual":
                fin_periodo = inicio_periodo + timedelta(days=365)
            elif plan.tipo == "Trimestral":
                fin_periodo = inicio_periodo + timedelta(days=90)
            else:
                fin_periodo = inicio_periodo + timedelta(days=30)
            
            # 4. Enviar email de bienvenida
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
            
            try:
                logger.info("📧 Enviando email de bienvenida...")
                send_mail(
                    subject, 
                    message, 
                    DEFAULT_FROM_EMAIL, 
                    [email],
                    fail_silently=False
                )
                logger.info(f"✅ Email enviado a {email}")
            except Exception as e:
                logger.error(f"❌ Error al enviar email: {str(e)}")
            
            # Resumen final
            total_time = time.time() - start_time
            logger.info("=" * 60)
            logger.info("✅ PROCESAMIENTO EN BACKGROUND COMPLETADO")
            logger.info(f"⏱️  TIEMPO TOTAL BACKGROUND: {total_time:.2f}s ({total_time/60:.2f} min)")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento background: {str(e)}", exc_info=True)
    
    @staticmethod
    @transaction.atomic
    def create_tenant_with_domain(validated: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea Tenant y Domain rápidamente, devuelve respuesta inmediata.
        Las migraciones y configuración se procesan en segundo plano.
        """
        start_time = time.time()
        logger.info("🚀 CREACIÓN RÁPIDA DE TENANT (sin migraciones)")
        
        nombre = validated["first_name"]
        apellido = validated["last_name"]
        email = validated["email"]
        nombre_empresa = validated["nombre_empresa"]
        username = validated["username"]
        schema_name = validated["schema_name"]
        full_domain = validated["domain"]
        plan = validated["plan"]

        if Domain.objects.filter(domain=full_domain).exists():
            raise ValueError("Dominio ya existente.")

        # 1. Crear tenant SIN schema (rápido - sin migraciones)
        logger.info(f"🔵 Creando registro de tenant '{schema_name}'...")
        tenant = Tenant(schema_name=schema_name, name=nombre_empresa)
        tenant.save()  # Rápido porque auto_create_schema=False
        logger.info(f"✅ Tenant creado (sin schema aún)")
        
        # 2. Crear dominio
        Domain.objects.create(domain=full_domain, tenant=tenant, is_primary=True)
        logger.info(f"✅ Dominio creado: {full_domain}")
        
        # 3. Calcular fechas de suscripción según el tipo de plan
        inicio_periodo = timezone.now().date()
        if plan.tipo == "Mensual":
            fin_periodo = inicio_periodo + timedelta(days=30)
        elif plan.tipo == "Anual":
            fin_periodo = inicio_periodo + timedelta(days=365)
        elif plan.tipo == "Trimestral":
            fin_periodo = inicio_periodo + timedelta(days=90)
        else:
            fin_periodo = inicio_periodo + timedelta(days=30)
        
        # 4. Crear suscripción en esquema público
        suscripcion = Suscripcion.objects.create(
            tenant=tenant,
            plan=plan,
            estado="activo",
            inicio_periodo=inicio_periodo,
            fin_periodo=fin_periodo
        )
        logger.info(f"✅ Suscripción creada: {plan.nombre}")
        
        # 5. Crear registro de uso del tenant
        UsoTenant.objects.create(tenant=tenant)
        logger.info("✅ Registro de uso creado")
        
        # 6. Iniciar procesamiento en segundo plano (migraciones + usuario + email)
        background_thread = threading.Thread(
            target=TenantFormService._process_tenant_background,
            args=(tenant.id, validated),
            daemon=True
        )
        background_thread.start()
        logger.info("🔄 Procesamiento en background iniciado (migraciones, usuario, email)")
        
        # Calcular tiempo de respuesta rápida
        response_time = time.time() - start_time
        logger.info("=" * 60)
        logger.info("✅ RESPUESTA RÁPIDA GENERADA")
        logger.info(f"⏱️  Tiempo de respuesta: {response_time:.2f}s")
        logger.info("🔄 Migraciones y configuración finalizarán en ~1-2 minutos")
        logger.info("📧 Recibirás un email cuando todo esté listo")
        logger.info("=" * 60)

        return {
            "tenant_id": tenant.id, #type:ignore
            "schema_name": tenant.schema_name,
            "domain": full_domain,
            "admin_username": username,
            "admin_email": email,
            "status": "processing",
            "message": f"¡Empresa '{nombre_empresa}' creada exitosamente! La configuración se completará en 1-2 minutos. Recibirás un email de confirmación cuando todo esté listo.",
            "tiempo_respuesta_segundos": round(response_time, 2),
            "procesamiento_background": True,
            "suscripcion": {
                "plan_nombre": plan.nombre,
                "plan_tipo": plan.get_tipo_display(),
                "precio": str(plan.precio),
                "inicio_periodo": inicio_periodo.isoformat(),
                "fin_periodo": fin_periodo.isoformat(),
                "estado": "activo",
                "max_hoteles": plan.max_hoteles,
                "max_usuarios": plan.max_usuarios,
            },
            "acceso": {
                "url": f"http://{full_domain}/authentication/login",
                "usuario": username,
                "nota": "Podrás acceder en 1-2 minutos cuando la configuración finalice"
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

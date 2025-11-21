from typing import Dict, Any
from django.db import transaction, connection
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from core.models import Tenant
from django.core.mail import send_mail
from config.settings import DEFAULT_FROM_EMAIL
from datetime import timedelta
from django.utils import timezone
from apps.suscripciones.models import Suscripcion, UsoTenant
import logging
import time
import threading

User = get_user_model()
logger = logging.getLogger(__name__)


class TenantFormService:
    """
    Servicio para manejar la creación de tenants desde formularios públicos.
    Ahora simplificado sin lógica de dominios.
    """
    
    @staticmethod
    @transaction.atomic
    def create_tenant_fast(validated: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea Tenant rápidamente y devuelve respuesta inmediata.
        Las migraciones y configuración se procesan en segundo plano.
        """
        start_time = time.time()
        logger.info("🚀 CREACIÓN RÁPIDA DE TENANT")
        
        # Extraer datos
        nombre = validated["first_name"]
        apellido = validated["last_name"]
        email = validated["email"]
        nombre_empresa = validated["nombre_empresa"]
        username = validated["username"]
        password = validated["password"]
        schema_name = validated["schema_name"]
        plan = validated["plan"]

        # Verificar que el schema no exista
        if Tenant.objects.filter(schema_name=schema_name).exists():
            raise ValueError(f"El código de empresa '{schema_name}' ya existe.")

        # 1. Crear tenant SIN schema (rápido - sin migraciones)
        logger.info(f"🔵 Creando registro de tenant '{schema_name}'...")
        tenant = Tenant(schema_name=schema_name, name=nombre_empresa)
        tenant.save()  # Rápido porque auto_create_schema=False
        logger.info(f"✅ Tenant creado (sin schema aún)")
        
        # 2. Calcular fechas de suscripción según el tipo de plan
        inicio_periodo = timezone.now().date()
        if plan.tipo == "Mensual":
            fin_periodo = inicio_periodo + timedelta(days=30)
        elif plan.tipo == "Anual":
            fin_periodo = inicio_periodo + timedelta(days=365)
        elif plan.tipo == "Trimestral":
            fin_periodo = inicio_periodo + timedelta(days=90)
        else:
            fin_periodo = inicio_periodo + timedelta(days=30)
        
        # 3. Crear suscripción en esquema público
        suscripcion = Suscripcion.objects.create(
            tenant=tenant,
            plan=plan,
            estado="activo",
            inicio_periodo=inicio_periodo,
            fin_periodo=fin_periodo
        )
        logger.info(f"✅ Suscripción creada: {plan.nombre}")
        
        # 4. Inicializar UsoTenant (solo contadores, no necesita periodos)
        UsoTenant.objects.create(
            tenant=tenant,
            hoteles=0,
            usuarios=0
        )
        logger.info(f"✅ UsoTenant inicializado")
        
        elapsed = time.time() - start_time
        logger.info(f"⏱️ Tenant creado en {elapsed:.2f}s (sin migraciones)")
        
        # 5. Iniciar proceso en background para crear schema y usuario
        logger.info(f"🔧 Iniciando creación de schema en background...")
        thread = threading.Thread(
            target=TenantFormService._create_schema_and_user_background,
            args=(tenant.id, schema_name, username, password, email, nombre, apellido)
        )
        thread.daemon = True
        thread.start()
        
        # 6. Retornar respuesta inmediata
        return {
            "tenant_id": tenant.id,
            "schema_name": schema_name,
            "admin_username": username,
            "admin_email": email,
            "message": "Tenant creado exitosamente. La configuración se completará en unos minutos.",
            "status": "creating"
        }
    
    @staticmethod
    def _create_schema_and_user_background(tenant_id, schema_name, username, password, email, nombre, apellido):
        """
        Proceso en background que crea el schema y el usuario admin.
        """
        try:
            logger.info(f"🔧 [Background] Iniciando creación de schema '{schema_name}'...")
            tenant = Tenant.objects.get(id=tenant_id)
            
            # Crear schema con migraciones
            logger.info(f"🔧 [Background] Ejecutando migraciones...")
            start = time.time()
            tenant.create_schema(check_if_exists=True)
            elapsed = time.time() - start
            logger.info(f"✅ [Background] Schema creado en {elapsed:.2f}s")
            
            # Crear usuario admin en el schema del tenant
            logger.info(f"👤 [Background] Creando usuario admin...")
            with schema_context(schema_name):
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=nombre,
                    last_name=apellido
                )
                user.is_staff = True
                user.is_superuser = True
                user.save()
                logger.info(f"✅ [Background] Usuario admin creado: {username}")
            
            # Enviar email de bienvenida
            TenantFormService._send_welcome_email(
                email, nombre, username, schema_name
            )
            
            logger.info(f"🎉 [Background] Tenant '{schema_name}' completamente configurado")
            
        except Exception as e:
            logger.error(f"❌ [Background] Error configurando tenant: {e}", exc_info=True)
    
    @staticmethod
    def _send_welcome_email(email: str, nombre: str, username: str, schema_name: str):
        """
        Envía email de bienvenida al nuevo tenant.
        """
        try:
            subject = f"🎉 Bienvenido a tu cuenta empresarial"
            message = f"""
Hola {nombre},

¡Tu cuenta empresarial ha sido creada exitosamente!

📋 Información de acceso:
━━━━━━━━━━━━━━━━━━━━━
👤 Usuario: {username}
🏢 Código de Empresa: {schema_name}

⚠️ IMPORTANTE: Guarda tu código de empresa, lo necesitarás para iniciar sesión.

Instrucciones de acceso:
1. Ve a la página de login
2. Ingresa tu código de empresa: {schema_name}
3. Ingresa tu usuario: {username}
4. Ingresa tu contraseña

¡Comienza a disfrutar de todas las funcionalidades!

Saludos,
El equipo de soporte
            """
            
            send_mail(
                subject,
                message,
                DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True
            )
            logger.info(f"📧 Email de bienvenida enviado a {email}")
        except Exception as e:
            logger.error(f"❌ Error enviando email: {e}")


class TenantService:
    """
    Servicio para operaciones generales de tenants (uso interno).
    """
    
    @staticmethod
    @transaction.atomic
    def create_tenant_basic(schema_name: str, name: str) -> Dict[str, Any]:

        if Tenant.objects.filter(schema_name=schema_name).exists():
            raise ValueError(f"El tenant '{schema_name}' ya existe.")
        
        tenant = Tenant(schema_name=schema_name, name=name)
        tenant.save()
        
        # Crear schema con migraciones
        tenant.create_schema(check_if_exists=True)
        
        logger.info(f"✅ Tenant básico creado: {schema_name}")
        
        return {
            "tenant_id": tenant.id,
            "schema_name": schema_name,
            "name": name,
            "message": "Tenant creado exitosamente"
        }

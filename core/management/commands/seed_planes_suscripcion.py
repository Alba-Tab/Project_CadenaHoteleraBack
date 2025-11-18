from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from apps.suscripciones.models import Plan, Suscripcion, TipoChoices, EstadoChoises, UsoTenant
from core.models import Tenant


class Command(BaseCommand):
    help = "Crea planes de suscripción y asigna una suscripción activa a un tenant"

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            type=str,
            help="Esquema del tenant al que se asignará la suscripción",
            required=True
        )

    def handle(self, *args, **options):
        schema = options["schema"]

        # ===========================
        # 1. CREAR PLANES
        # ===========================
        self.stdout.write(self.style.SUCCESS("== Creando Planes =="))

        planes_definidos = [
            {
                "nombre": "Plan Gratis",
                "max_usuarios": 3,
                "max_hoteles": 1,
                "precio": 0,
                "tipo": TipoChoices.MENSUAL,
            },
            {
                "nombre": "Plan Starter",
                "max_usuarios": 10,
                "max_hoteles": 1,
                "precio": 9.99,
                "tipo": TipoChoices.MENSUAL,
            },
            {
                "nombre": "Plan Estándar",
                "max_usuarios": 25,
                "max_hoteles": 3,   # ← solicitado
                "precio": 24.99,
                "tipo": TipoChoices.MENSUAL,
            },
            {
                "nombre": "Plan Pro + App Móvil",
                "max_usuarios": 50,
                "max_hoteles": 4,   # ← solicitado
                "precio": 49.99,
                "tipo": TipoChoices.MENSUAL,
            },
        ]

        planes_creados = []
        for data in planes_definidos:
            plan, created = Plan.objects.get_or_create(
                nombre=data["nombre"],
                tipo=data["tipo"],
                defaults=data
            )
            planes_creados.append(plan)
            self.stdout.write(f"✔ {plan.nombre} ({'creado' if created else 'existente'})")

        # Plan asignado por defecto para el tenant
        plan_asignado = next(p for p in planes_creados if p.nombre == "Plan Gratis")

        # ===========================
        # 2. OBTENER EL TENANT
        # ===========================
        try:
            tenant = Tenant.objects.get(schema_name=schema)
        except Tenant.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ No existe el tenant: {schema}"))
            return

        # ===========================
        # 3. CREAR SUSCRIPCIÓN
        # ===========================
        self.stdout.write(self.style.SUCCESS("\n== Creando Suscripción =="))

        inicio = timezone.now().date()
        fin = inicio + timedelta(days=30)

        sus, created = Suscripcion.objects.get_or_create(
            tenant=tenant,
            defaults={
                "plan": plan_asignado,
                "estado": EstadoChoises.ACTIVO,
                "inicio_periodo": inicio,
                "fin_periodo": fin,
            }
        )

        if not created:
            sus.plan = plan_asignado
            sus.estado = EstadoChoises.ACTIVO
            sus.inicio_periodo = inicio
            sus.fin_periodo = fin
            sus.save()

        self.stdout.write(f"✔ Suscripción activa para {tenant.schema_name}")

        # ===========================
        # 4. CREAR UsoTenant
        # ===========================
        uso, created = UsoTenant.objects.get_or_create(tenant=tenant)

        self.stdout.write(f"✔ UsoTenant creado (Hoteles={uso.hoteles}, Usuarios={uso.usuarios})")

        # ===========================
        # FIN
        # ===========================
        self.stdout.write(self.style.SUCCESS("\n🎉 Seeder completado con éxito 🚀"))

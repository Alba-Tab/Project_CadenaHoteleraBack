"""
Comando para recalcular el contador de usuarios en UsoTenant.
Útil cuando el contador se desincroniza con la realidad.

Uso:
    python manage.py recalcular_uso_usuarios
    python manage.py recalcular_uso_usuarios --tenant=nombre_schema
"""
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from core.models import Tenant
from apps.suscripciones.models import UsoTenant
from apps.usuarios.models import User
from django.utils import timezone


class Command(BaseCommand):
    help = 'Recalcula el contador de usuarios en UsoTenant para todos los tenants o uno específico'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            help='Schema name del tenant específico a recalcular (opcional)',
        )

    def handle(self, *args, **options):
        tenant_name = options.get('tenant')

        if tenant_name:
            # Recalcular solo un tenant específico
            try:
                with schema_context('public'):
                    tenant = Tenant.objects.get(schema_name=tenant_name)
                self.recalcular_tenant(tenant)
            except Tenant.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Tenant "{tenant_name}" no encontrado')
                )
                return
        else:
            # Recalcular todos los tenants
            with schema_context('public'):
                tenants = Tenant.objects.exclude(schema_name='public')
                total = tenants.count()
                
            self.stdout.write(f'\n📊 Recalculando uso de usuarios para {total} tenants...\n')
            
            for tenant in tenants:
                self.recalcular_tenant(tenant)
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Recálculo completado para {total} tenants')
            )

    def recalcular_tenant(self, tenant):
        """Recalcula el contador de usuarios de un tenant específico"""
        try:
            # Contar usuarios en el schema del tenant
            with schema_context(tenant.schema_name):
                total_usuarios = User.objects.count()
            
            # Actualizar UsoTenant
            with schema_context('public'):
                uso, created = UsoTenant.objects.get_or_create(
                    tenant=tenant,
                    defaults={
                        'usuarios': total_usuarios,
                        'hoteles': 0,
                        'ultima_actualizacion': timezone.now()
                    }
                )
                
                if not created:
                    valor_anterior = uso.usuarios
                    uso.usuarios = total_usuarios
                    uso.ultima_actualizacion = timezone.now()
                    uso.save(update_fields=['usuarios', 'ultima_actualizacion'])
                    
                    if valor_anterior != total_usuarios:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✅ {tenant.schema_name}: {valor_anterior} → {total_usuarios} usuarios'
                            )
                        )
                    else:
                        self.stdout.write(
                            f'  ⚪ {tenant.schema_name}: {total_usuarios} usuarios (sin cambios)'
                        )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✨ {tenant.schema_name}: Creado con {total_usuarios} usuarios'
                        )
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'  ❌ {tenant.schema_name}: Error - {str(e)}'
                )
            )

from django.apps import apps as django_apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def register_audit_models_after_migrate(sender, **kwargs):

    if not django_apps.ready:
        return 

    try:
        from django_tenants.utils import schema_context, get_tenant_model
        from .audit_registry import register_audit_models

        TenantModel = get_tenant_model()
        for tenant in TenantModel.objects.all():
            with schema_context(tenant.schema_name):
                register_audit_models()

        print("Modelos de auditoría registrados correctamente en todos los tenants.")

    except Exception as e:
        print(f"No se pudo registrar la auditoría: {e}")

from django.contrib import admin
from django.utils.html import format_html
from core.models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """
    Administración de Tenants (Esquemas)
    """
    list_display = [
        'schema_name', 'name', 'suscripcion_activa', 
        'on_trial_badge', 'paid_until'
    ]
    list_filter = ['on_trial', 'paid_until']
    search_fields = ['schema_name', 'name']
    ordering = ['schema_name']
    readonly_fields = ['schema_name']
    
    fieldsets = (
        ('Información del Tenant', {
            'fields': ('schema_name', 'name'),
            'description': 'Schema name es el identificador único del tenant (código de empresa)'
        }),
        ('Estado', {
            'fields': ('on_trial', 'paid_until'),
            'description': 'Estado del tenant y fechas de pago'
        }),
    )
    
    def suscripcion_activa(self, obj):
        """Muestra la suscripción activa del tenant"""
        from apps.suscripciones.models import Suscripcion
        from django_tenants.utils import schema_context
        
        with schema_context("public"):
            suscripcion = Suscripcion.objects.filter(
                tenant=obj,
                estado__in=['activo', 'prueba']
            ).first()
            
            if suscripcion:
                color = '#2ecc71' if suscripcion.estado == 'activo' else '#3498db'
                return format_html(
                    '<span style="background-color: {}; color: white; '
                    'padding: 3px 8px; border-radius: 3px; font-size: 11px;">'
                    '{} - {}</span>',
                    color,
                    suscripcion.plan.nombre,
                    suscripcion.get_estado_display()
                )
        return format_html('<span style="color: #e74c3c;">Sin suscripción</span>')
    suscripcion_activa.short_description = 'Suscripción'
    
    def on_trial_badge(self, obj):
        """Badge para indicar si está en prueba"""
        if obj.on_trial:
            return format_html(
                '<span style="background-color: #f39c12; color: white; '
                'padding: 2px 8px; border-radius: 3px; font-size: 11px;">⚡ Prueba</span>'
            )
        return format_html('<span style="color: #95a5a6;">-</span>')
    on_trial_badge.short_description = 'Trial'


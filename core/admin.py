from django.contrib import admin
from django.utils.html import format_html
from core.models import Tenant, Domain


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """
    Administración de Tenants (Esquemas)
    """
    list_display = [
        'schema_name', 'name', 'dominios', 'suscripcion_activa', 
        'on_trial_badge', 'paid_until'
    ]
    list_filter = ['on_trial', 'paid_until']
    search_fields = ['schema_name', 'name']
    ordering = ['schema_name']
    readonly_fields = ['schema_name']
    
    fieldsets = (
        ('Información del Tenant', {
            'fields': ('schema_name', 'name')
        }),
        ('Estado', {
            'fields': ('on_trial', 'paid_until'),
            'description': 'Estado del tenant y fechas de pago'
        }),
    )
    
    def dominios(self, obj):
        """Muestra los dominios asociados"""
        domains = obj.domains.all()
        if domains:
            domain_list = '<br>'.join([
                f'{"🌐 " if d.is_primary else "  "}{d.domain}'
                for d in domains
            ])
            return format_html(domain_list)
        return '-'
    dominios.short_description = 'Dominios'
    
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


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """
    Administración de Dominios
    """
    list_display = [
        'domain', 'tenant_info', 'is_primary_badge'
    ]
    list_filter = ['is_primary']
    search_fields = ['domain', 'tenant__schema_name', 'tenant__name']
    ordering = ['domain']
    
    fieldsets = (
        ('Información del Dominio', {
            'fields': ('domain', 'tenant', 'is_primary')
        }),
    )
    
    def tenant_info(self, obj):
        """Muestra información del tenant"""
        return format_html(
            '<strong>{}</strong><br><small style="color: #666;">{}</small>',
            obj.tenant.name,
            obj.tenant.schema_name
        )
    tenant_info.short_description = 'Tenant'
    
    def is_primary_badge(self, obj):
        """Badge para dominio primario"""
        if obj.is_primary:
            return format_html(
                '<span style="background-color: #3498db; color: white; '
                'padding: 2px 8px; border-radius: 3px; font-size: 11px;">⭐ Primario</span>'
            )
        return format_html('<span style="color: #95a5a6;">Secundario</span>')
    is_primary_badge.short_description = 'Tipo'
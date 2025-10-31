from django.contrib import admin
from django.utils.html import format_html
from .models import Suscripcion, Plan, UsoTenant


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """
    Administración de Planes de Suscripción
    """
    list_display = [
        'id', 'nombre', 'tipo_badge', 'precio_formateado', 
        'max_hoteles', 'max_usuarios', 'activo_badge'
    ]
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre']
    ordering = ['nombre', 'tipo']
    list_editable = []
    
    fieldsets = (
        ('Información del Plan', {
            'fields': ('nombre', 'activo')
        }),
        ('Límites de Recursos', {
            'fields': ('max_usuarios', 'max_hoteles'),
            'description': 'Define los límites máximos de recursos para este plan'
        }),
        ('Precio y Duración', {
            'fields': ('precio', 'tipo'),
            'description': 'Configura el precio y tipo de suscripción'
        }),
    )
    
    def tipo_badge(self, obj):
        """Muestra el tipo con un badge de color"""
        colores = {
            'Mensual': '#3498db',
            'Anual': '#2ecc71',
            'T': '#f39c12'  # Trimestral
        }
        color = colores.get(obj.tipo, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_tipo_display()
        )
    tipo_badge.short_description = 'Tipo'
    
    def precio_formateado(self, obj):
        """Muestra el precio con formato de moneda"""
        return format_html('<strong>${:.2f}</strong>', obj.precio)
    precio_formateado.short_description = 'Precio'
    
    def activo_badge(self, obj):
        """Muestra estado activo con colores"""
        if obj.activo:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Activo</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Inactivo</span>'
        )
    activo_badge.short_description = 'Estado'


@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    """
    Administración de Suscripciones de Tenants
    """
    list_display = [
        'id', 'tenant_nombre', 'plan_nombre', 'estado_badge', 
        'inicio_periodo', 'fin_periodo', 'dias_restantes_display'
    ]
    list_filter = ['estado', 'plan', 'inicio_periodo']
    search_fields = ['tenant__schema_name', 'tenant__name', 'plan__nombre']
    ordering = ['-inicio_periodo']
    date_hierarchy = 'inicio_periodo'
    readonly_fields = ['tenant', 'inicio_periodo']
    
    fieldsets = (
        ('Información de la Suscripción', {
            'fields': ('tenant', 'plan', 'estado')
        }),
        ('Período de Vigencia', {
            'fields': ('inicio_periodo', 'fin_periodo'),
            'description': 'Fechas de inicio y fin de la suscripción'
        }),
    )
    
    def tenant_nombre(self, obj):
        """Muestra el nombre del tenant con link"""
        return format_html(
            '<strong>{}</strong><br><small style="color: #666;">{}</small>',
            obj.tenant.name,
            obj.tenant.schema_name
        )
    tenant_nombre.short_description = 'Tenant'
    
    def plan_nombre(self, obj):
        """Muestra el plan con detalles"""
        return format_html(
            '{}<br><small style="color: #666;">{} - ${:.2f}</small>',
            obj.plan.nombre,
            obj.plan.get_tipo_display(),
            obj.plan.precio
        )
    plan_nombre.short_description = 'Plan'
    
    def estado_badge(self, obj):
        """Muestra el estado con colores"""
        colores = {
            'activo': ('#2ecc71', '✓'),
            'prueba': ('#3498db', '⚡'),
            'vencido': ('#e74c3c', '✗'),
            'pausado': ('#f39c12', '⏸'),
            'cancelado': ('#95a5a6', '⊗')
        }
        color, icono = colores.get(obj.estado, ('#95a5a6', '?'))
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{} {}</span>',
            color,
            icono,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def dias_restantes_display(self, obj):
        """Muestra días restantes con colores"""
        from django.utils import timezone
        if obj.fin_periodo:
            delta = obj.fin_periodo - timezone.now().date()
            dias = max(0, delta.days)
            
            if dias > 30:
                color = 'green'
            elif dias > 7:
                color = 'orange'
            else:
                color = 'red'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} días</span>',
                color,
                dias
            )
        return '-'
    dias_restantes_display.short_description = 'Días Restantes'


@admin.register(UsoTenant)
class UsoTenantAdmin(admin.ModelAdmin):
    """
    Administración de Uso de Recursos por Tenant
    """
    list_display = [
        'id', 'tenant_nombre', 'hoteles_uso', 'usuarios_uso', 
        'ultima_actualizacion'
    ]
    list_filter = ['ultima_actualizacion']
    search_fields = ['tenant__schema_name', 'tenant__name']
    ordering = ['-ultima_actualizacion']
    readonly_fields = ['tenant', 'ultima_actualizacion']
    
    fieldsets = (
        ('Tenant', {
            'fields': ('tenant',)
        }),
        ('Uso de Recursos', {
            'fields': ('hoteles', 'usuarios'),
            'description': 'Contadores de recursos utilizados por el tenant'
        }),
        ('Información', {
            'fields': ('ultima_actualizacion',),
        }),
    )
    
    def tenant_nombre(self, obj):
        """Muestra el tenant con su suscripción"""
        suscripcion = obj.tenant.suscripciones.filter(
            estado__in=['activo', 'prueba']
        ).first()
        
        if suscripcion:
            return format_html(
                '<strong>{}</strong><br>'
                '<small style="color: #666;">{} - {}</small>',
                obj.tenant.name,
                obj.tenant.schema_name,
                suscripcion.plan.nombre
            )
        return format_html(
            '<strong>{}</strong><br><small style="color: #666;">{}</small>',
            obj.tenant.name,
            obj.tenant.schema_name
        )
    tenant_nombre.short_description = 'Tenant'
    
    def hoteles_uso(self, obj):
        """Muestra uso de hoteles con porcentaje"""
        suscripcion = obj.tenant.suscripciones.filter(
            estado__in=['activo', 'prueba']
        ).first()
        
        if suscripcion:
            limite = suscripcion.plan.max_hoteles
            porcentaje = (obj.hoteles / limite * 100) if limite > 0 else 0
            
            if porcentaje >= 90:
                color = 'red'
            elif porcentaje >= 70:
                color = 'orange'
            else:
                color = 'green'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} / {}</span> '
                '<small style="color: #666;">({:.0f}%)</small>',
                color,
                obj.hoteles,
                limite,
                porcentaje
            )
        return str(obj.hoteles)
    hoteles_uso.short_description = 'Hoteles'
    
    def usuarios_uso(self, obj):
        """Muestra uso de usuarios con porcentaje"""
        suscripcion = obj.tenant.suscripciones.filter(
            estado__in=['activo', 'prueba']
        ).first()
        
        if suscripcion:
            limite = suscripcion.plan.max_usuarios
            porcentaje = (obj.usuarios / limite * 100) if limite > 0 else 0
            
            if porcentaje >= 90:
                color = 'red'
            elif porcentaje >= 70:
                color = 'orange'
            else:
                color = 'green'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} / {}</span> '
                '<small style="color: #666;">({:.0f}%)</small>',
                color,
                obj.usuarios,
                limite,
                porcentaje
            )
        return str(obj.usuarios)
    usuarios_uso.short_description = 'Usuarios'

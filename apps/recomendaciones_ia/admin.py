from django.contrib import admin
from .models import RecomendacionPrecio, HistorialRecomendacion


@admin.register(RecomendacionPrecio)
class RecomendacionPrecioAdmin(admin.ModelAdmin):
    list_display = ['habitacion', 'tarifa_actual', 'tarifa_sugerida', 'confianza', 'aceptada', 'fecha_generacion']
    list_filter = ['aceptada', 'aplicada', 'fecha_generacion']
    search_fields = ['habitacion__numero', 'habitacion__tipo']
    readonly_fields = ['fecha_generacion']
    ordering = ['-fecha_generacion']


@admin.register(HistorialRecomendacion)
class HistorialRecomendacionAdmin(admin.ModelAdmin):
    list_display = ['habitacion', 'tarifa_anterior', 'tarifa_nueva', 'cambio_porcentaje', 'aceptado_por', 'fecha_aceptacion']
    list_filter = ['fecha_aceptacion']
    search_fields = ['habitacion__numero', 'habitacion__tipo']
    readonly_fields = ['fecha_aceptacion', 'cambio_porcentaje']
    ordering = ['-fecha_aceptacion']

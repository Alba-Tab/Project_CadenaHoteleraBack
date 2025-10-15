from django.contrib import admin
from .models import Pago

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("id", "estado", "fecha_pago", "metodo", "monto", "referencia", "created_at")
    list_filter = ("estado", "metodo", "fecha_pago")
    search_fields = ("referencia", "metodo")
    ordering = ("-fecha_pago", "-id")
    

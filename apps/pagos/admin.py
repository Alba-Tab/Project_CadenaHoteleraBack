from django.contrib import admin
from .models import Pago

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("id", "estado", "fecha_pago", "metodo", "monto", "referencia", "folio_estancia")
    list_filter = ("estado", "metodo", "fecha_pago")
    search_fields = ("referencia", "metodo")
    ordering = ("-fecha_pago", "-id")

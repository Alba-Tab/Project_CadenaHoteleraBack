from django.contrib import admin

from .models import Servicio

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "tipo", "precio", "created_at")
    search_fields = ("nombre", "tipo")
    list_filter = ("tipo",)

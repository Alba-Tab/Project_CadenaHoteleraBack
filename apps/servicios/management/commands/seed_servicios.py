from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.servicios.models import Servicio

class Command(BaseCommand):
    help = "Crea servicios de ejemplo dentro del schema actual (tenant actual)."

    def handle(self, *args, **kwargs):
        data = [
            {"nombre": "Lavandería", "descripcion": "Lavado por kg", "precio": Decimal("15.50"), "tipo": "extra"},
            {"nombre": "Desayuno Buffet", "descripcion": "7:00-10:00", "precio": Decimal("30.00"), "tipo": "alimento"},
            {"nombre": "Traslado Aeropuerto", "descripcion": "Ida o vuelta", "precio": Decimal("60.00"), "tipo": "transporte"},
        ]
        for d in data:
            Servicio.objects.get_or_create(nombre=d["nombre"], defaults=d)
        self.stdout.write(self.style.SUCCESS("✅ Servicios de ejemplo creados o verificados."))

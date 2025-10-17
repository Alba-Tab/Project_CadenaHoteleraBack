from django.core.management.base import BaseCommand
from apps.pagos.models import Pago
from apps.folioestancias.models import FolioEstancia
from datetime import date
from decimal import Decimal

class Command(BaseCommand):
    help = "Crea pagos de ejemplo para el tenant actual."

    def handle(self, *args, **options):
        folio = FolioEstancia.objects.first()
        data = [
            {"estado": "pendiente", "fecha_pago": date(2025,10,15), "metodo": "tarjeta crédito", "monto": Decimal("180.00"), "referencia": "TXN-TAJ-001", "folio_estancia": folio},
            {"estado": "completado", "fecha_pago": date(2025,10,14), "metodo": "efectivo", "monto": Decimal("220.00"), "referencia": "TXN-TAJ-002", "folio_estancia": folio},
        ]
        for d in data:
            Pago.objects.get_or_create(referencia=d["referencia"], defaults=d)
        self.stdout.write(self.style.SUCCESS("✅ Pagos de ejemplo creados."))
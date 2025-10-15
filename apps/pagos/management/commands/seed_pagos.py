from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.pagos.models import Pago
from datetime import date

class Command(BaseCommand):
    help = "Crea datos de ejemplo para la tabla Pago dentro del schema actual (tenant actual)."

    def handle(self, *args, **kwargs):
        data = [
            {
                "estado": "pendiente",
                "fecha_pago": date(2025, 10, 15),
                "metodo": "tarjeta de crédito",
                "monto": Decimal("250.50"),
                "referencia": "TXN-HOTEL-001",
                "folio_estancia": None,
            },
            {
                "estado": "completado",
                "fecha_pago": date(2025, 10, 14),
                "metodo": "efectivo",
                "monto": Decimal("180.00"),
                "referencia": "EFV-HOTEL-002",
                "folio_estancia": None,
            },
            {
                "estado": "fallido",
                "fecha_pago": date(2025, 10, 13),
                "metodo": "transferencia bancaria",
                "monto": Decimal("300.00"),
                "referencia": "TRF-HOTEL-003",
                "folio_estancia": None,
            },
            {
                "estado": "completado",
                "fecha_pago": date(2025, 10, 10),
                "metodo": "tarjeta débito",
                "monto": Decimal("120.00"),
                "referencia": "DBT-HOTEL-004",
                "folio_estancia": None,
            },
            {
                "estado": "pendiente",
                "fecha_pago": date(2025, 10, 16),
                "metodo": "PayPal",
                "monto": Decimal("99.99"),
                "referencia": "PAY-HOTEL-005",
                "folio_estancia": None,
            },
        ]

        created_count = 0
        for d in data:
            pago, created = Pago.objects.get_or_create(
                referencia=d["referencia"],
                defaults=d
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ {created_count} pagos creados o verificados correctamente."
        ))

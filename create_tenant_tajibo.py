#!/usr/bin/env python
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Tenant, Domain

def create_tenant(schema_name, name, domain_url):
    tenant = Tenant(
        schema_name=schema_name,
        name=name,
        paid_until=date(2026, 1, 1),
        on_trial=False
    )
    tenant.save()  # 🔹 esto crea automáticamente el schema en PostgreSQL

    domain = Domain()
    domain.domain = domain_url
    domain.tenant = tenant
    domain.is_primary = True
    domain.save()

    print(f"✅ Tenant '{name}' creado con schema '{schema_name}' y dominio '{domain_url}'")

if __name__ == "__main__":
    # Cambia estos valores según tu hotel
    create_tenant(
        schema_name="hotel_tajibo",
        name="Hotel tajibo",
        domain_url="hoteltajibo.localhost"
    )

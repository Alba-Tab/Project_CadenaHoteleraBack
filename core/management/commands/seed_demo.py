import random
from datetime import timedelta, datetime
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.db import connection

from apps.hoteles.models import Hotel
from apps.habitaciones.models import Habitacion
from apps.usuarios.models import User
from apps.reservas.models import Reserva
from apps.checkinout.models import CheckInOut
from apps.folioestancias.models import FolioEstancia
from apps.pagos.models import Pago


class Command(BaseCommand):
    help = "Genera datos de prueba (hoteles, habitaciones, usuarios, reservas, check-in/out, folios y pagos)"

    def handle(self, *args, **kwargs):
        schema = connection.schema_name
        self.stdout.write(self.style.SUCCESS(f"🔥 Sembrando datos en tenant: {schema}"))

        # ============================
        # 1️⃣ USUARIOS DE PRUEBA
        # ============================
        user1, _ = User.objects.get_or_create(
            username="huesped1",
            defaults={
                "email": "huesped1@test.com",
            }
        )
        user1.set_password("123456")
        user1.save()

        user2, _ = User.objects.get_or_create(
            username="huesped2",
            defaults={
                "email": "huesped2@test.com",
            }
        )
        user2.set_password("123456")
        user2.save()

        self.stdout.write(self.style.SUCCESS("✔ Usuarios creados."))

        # ============================
        # 2️⃣ HOTELES
        # ============================

        hotel1, _ = Hotel.objects.get_or_create(
            id=1,
            defaults={
                "nombre": "Hotel Sol",
                "telefono": "70000000",
                "direccion": "Av. Principal #123",
                "ciudad": "Santa Cruz",
                "pais": "Bolivia",
                "estado": "Activo",
            },
        )

        hotel2, _ = Hotel.objects.get_or_create(
            nombre="Hotel Luna",
            defaults={
                "telefono": "75555555",
                "direccion": "Zona Central",
                "ciudad": "Santa Cruz",
                "pais": "Bolivia",
                "estado": "Activo",
            }
        )

        self.stdout.write(self.style.SUCCESS("✔ Hoteles creados."))

        # ============================
        # 3️⃣ HABITACIONES (10 por hotel)
        # ============================

        def crear_habitaciones(hotel):
            habitaciones = []
            for i in range(1, 11):
                hab, _ = Habitacion.objects.get_or_create(
                    hotel=hotel,
                    numero=f"{i:03}",
                    defaults={
                        "capacidad": "2",
                        "descripcion": "Habitación de prueba",
                        "precio_noche": random.choice([100, 120, 150, 80]),
                        "estado": Habitacion.DISPONIBLE,
                        "tamanio": "30m2",
                        "tipo": random.choice(["doble", "suite", "individual"]),
                    },
                )
                habitaciones.append(hab)
            return habitaciones

        habs1 = crear_habitaciones(hotel1)
        habs2 = crear_habitaciones(hotel2)

        self.stdout.write(self.style.SUCCESS("✔ Habitaciones creadas."))

        # ============================
        # 4️⃣ RESERVAS (20 por hotel)
        # ============================

        def crear_reservas(hotel, habitaciones):
            reservas = []
            for _ in range(20):
                hab = random.choice(habitaciones)

                dias_antes = random.randint(1, 40)
                duracion = random.randint(1, 4)

                fecha_entrada = now().date() - timedelta(days=dias_antes)
                fecha_salida = fecha_entrada + timedelta(days=duracion)

                reserva = Reserva.objects.create(
                    fecha_entrada=fecha_entrada,
                    fecha_salida=fecha_salida,
                    total=hab.precio_noche * duracion,
                    estado=Reserva.REALIZADA,
                    habitacion=hab,
                    huesped=random.choice([user1, user2]),
                    hotel=hotel,
                )

                reservas.append(reserva)

            return reservas

        reservas1 = crear_reservas(hotel1, habs1)
        reservas2 = crear_reservas(hotel2, habs2)

        self.stdout.write(self.style.SUCCESS("✔ Reservas creadas."))

        # ============================
        # 5️⃣ CHECK-IN / CHECK-OUT
        # ============================

        def crear_checkin_out(reservas):
            for r in reservas:
                hora_in = datetime.now().time().replace(hour=14, minute=0)

                CheckInOut.objects.create(
                    reserva=r,
                    fecha_checkin=r.fecha_entrada,
                    hora_checkin=hora_in,
                    fecha_checkout=r.fecha_salida,
                    hora_checkout=hora_in.replace(hour=11),
                    observaciones="Check-in automático de prueba"
                )

        crear_checkin_out(reservas1)
        crear_checkin_out(reservas2)

        self.stdout.write(self.style.SUCCESS("✔ Check-in/out creados."))

        # ============================
        # 6️⃣ FOLIOS + PAGOS
        # ============================

        def crear_folios_pagos(reservas):
            for r in reservas:
                folio = FolioEstancia.objects.create(
                    estado=FolioEstancia.PAGADO,
                    total_pagado=r.total,
                    huesped=r.huesped,
                    reserva=r,
                )

                Pago.objects.create(
                    estado=Pago.ESTADO_COMPLETADO,
                    metodo="efectivo",
                    monto=r.total,
                    referencia=f"Pago-{r.id}",
                    folio_estancia=folio,
                )

        crear_folios_pagos(reservas1)
        crear_folios_pagos(reservas2)

        self.stdout.write(self.style.SUCCESS("✔ Folios y pagos creados."))
        self.stdout.write(self.style.SUCCESS("🎉 Seeder completado con éxito"))

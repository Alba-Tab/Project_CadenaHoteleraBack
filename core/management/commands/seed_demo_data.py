import random
from datetime import timedelta, datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import connection

from apps.hoteles.models import Hotel
from apps.habitaciones.models import Habitacion
from apps.reservas.models import Reserva
from apps.checkinout.models import CheckInOut
from apps.folioestancias.models import FolioEstancia
from apps.pagos.models import Pago
from apps.servicios.models import Servicio
from apps.servicios_asociados.models import ServiciosAsociados
from apps.fidelizacion.models import ProgramaFidelizacion, CuentaFidelizacion

User = get_user_model()


class Command(BaseCommand):
    help = "Genera un SEEDER MASIVO para pruebas reales de un hotel SaaS"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("===== INICIANDO SEEDER MASIVO ====="))

        # ==========================================================
        # USAR SCHEMA DEL TENANT
        # ==========================================================
        connection.set_schema("hotel_sol", True)
        self.stdout.write(self.style.WARNING("Usando schema: hotel_sol"))

        # ==========================================================
        # 1. USUARIOS
        # ==========================================================
        users = []
        for i in range(25):
            user, created = User.objects.get_or_create(
                username=f"user{i}",
                defaults={
                    "email": f"user{i}@test.com",
                    "password": "12345",
                }
            )
            users.append(user)

        self.stdout.write(self.style.SUCCESS("✔ 25 usuarios creados"))

        # ==========================================================
        # 2. HOTELES
        # ==========================================================
        hoteles = []
        for i in range(3):
            hotel, created = Hotel.objects.get_or_create(
                nombre=f"Hotel Demo {i+1}",
                defaults={
                    "telefono": f"70012{i}45",
                    "direccion": f"Avenida Test #{100+i}",
                    "ciudad": "Santa Cruz",
                    "pais": "Bolivia",
                    "estado": "Activo"
                }
            )
            hoteles.append(hotel)

        self.stdout.write(self.style.SUCCESS("✔ 3 Hoteles generados"))

        # ==========================================================
        # 3. HABITACIONES (20 por hotel)
        # ==========================================================
        habitaciones = []
        tipos = ["individual", "doble", "suite", "deluxe", "familiar"]
        base_precios = {
            "individual": 150,
            "doble": 220,
            "suite": 350,
            "deluxe": 450,
            "familiar": 500
        }

        for hotel in hoteles:
            for i in range(20):
                tipo = random.choice(tipos)
                precio = base_precios[tipo] + random.randint(-20, 50)

                hab, created = Habitacion.objects.get_or_create(
                    hotel=hotel,
                    numero=str(100 + len(habitaciones)),
                    defaults={
                        "capacidad": str(random.choice([2, 3, 4])),
                        "descripcion": f"Habitación tipo {tipo}",
                        "precio_noche": precio,
                        "estado": Habitacion.DISPONIBLE,
                        "tamanio": f"{random.randint(25, 45)}m2",
                        "tipo": tipo,
                    }
                )
                habitaciones.append(hab)

        self.stdout.write(self.style.SUCCESS("✔ 60 Habitaciones generadas"))

        # ==========================================================
        # 4. SERVICIOS
        # ==========================================================
        lista_servicios = [
            ("Spa", 50),
            ("Desayuno buffet", 25),
            ("Cena gourmet", 60),
            ("Lavandería", 15),
            ("Transporte aeropuerto", 40),
            ("Tours turísticos", 75),
            ("Bar", 35)
        ]

        servicios = []
        for nombre, precio in lista_servicios:
            s, created = Servicio.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "descripcion": f"Servicio de {nombre.lower()}",
                    "precio": precio,
                    "tipo": "extra"
                }
            )
            servicios.append(s)

        self.stdout.write(self.style.SUCCESS("✔ 7 servicios creados"))

        # ==========================================================
        # 5. FIDELIZACIÓN
        # ==========================================================
        prog, created = ProgramaFidelizacion.objects.get_or_create(
            nombre="Fidelización Premium",
            defaults={
                "descripcion": "Acumula puntos por estancia.",
                "descuento_maximo": 50,
                "puntos_por_dolar_descuento": 10
            }
        )

        for user in users:
            CuentaFidelizacion.objects.get_or_create(
                cliente=user,
                fidelizacion=prog,
                defaults={"puntos_acumulados": random.randint(10, 500)}
            )

        self.stdout.write(self.style.SUCCESS("✔ Fidelización asignada"))

        # ==========================================================
        # 6. 200 RESERVAS COMPLETAS (VARIOS ESTADOS)
        # ==========================================================
        estados_reserva = [
            Reserva.REALIZADA,
            Reserva.PENDIENTE,
            Reserva.CANCELADA,
            Reserva.CONFIRMADA
        ]

        for _ in range(200):
            user = random.choice(users)
            hab = random.choice(habitaciones)

            dias_atras = random.randint(1, 120)
            entrada = timezone.now().date() - timedelta(days=dias_atras)
            noches = random.randint(1, 5)
            salida = entrada + timedelta(days=noches)

            estado = random.choice(estados_reserva)

            reserva = Reserva.objects.create(
                fecha_entrada=entrada,
                fecha_salida=salida,
                total=hab.precio_noche * noches,
                estado=estado,
                habitacion=hab,
                huesped=user,
                hotel=hab.hotel
            )

            # Solo crear check-in/out si aplica
            if estado in [Reserva.REALIZADA, Reserva.CONFIRMADA, Reserva.PENDIENTE]:
                CheckInOut.objects.create(
                    reserva=reserva,
                    fecha_checkin=entrada,
                    hora_checkin=datetime.now().time(),
                    fecha_checkout=salida,
                    hora_checkout=datetime.now().time(),
                )

            # Folio
            folio = FolioEstancia.objects.create(
                reserva=reserva,
                huesped=user,
                total_pagado=reserva.total if estado == Reserva.REALIZADA else 0,
                estado=FolioEstancia.PAGADO if estado == Reserva.REALIZADA else FolioEstancia.PENDIENTE
            )

            # Servicios Random
            for _ in range(random.randint(0, 4)):
                servicio = random.choice(servicios)
                ServiciosAsociados.objects.create(
                    servicio=servicio,
                    reserva=reserva,
                    folioestancia=folio,
                    cantidad=random.randint(1, 3),
                    estado="completado"
                )

            # Pagos
            estados_pago = [
                Pago.ESTADO_COMPLETADO, Pago.ESTADO_PENDIENTE,
            ]

            Pago.objects.create(
                estado=random.choice(estados_pago),
                metodo=random.choice(["tarjeta", "efectivo", "transferencia", "qr"]),
                monto=folio.total_pagado,
                referencia=f"PAY-{random.randint(10000,99999)}",
                folio_estancia=folio
            )

        self.stdout.write(self.style.SUCCESS(" 200 Reservas generadas con éxito"))
        self.stdout.write(self.style.SUCCESS("===== SEEDER COMPLETO  ====="))

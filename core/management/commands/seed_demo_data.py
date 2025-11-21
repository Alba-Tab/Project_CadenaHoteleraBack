import random
from datetime import timedelta, datetime, date

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import connection

from django_tenants.utils import get_tenant_model

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
    help = "Genera datos demo REALISTAS para TODOS los tenants (hotel SaaS)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            type=str,
            help="Schema del tenant a poblar (opcional, si no se pasa se procesan todos)",
        )
        parser.add_argument(
            "--reservas",
            type=int,
            default=300,
            help="Cantidad de reservas a generar por tenant (default: 300)",
        )

    # ============================
    #  Helpers de temporada
    # ============================
    def _get_temporada(self, mes: int) -> str:
        """
        Retorna 'alta', 'media' o 'baja' según el mes.
        Adaptado para Bolivia / Latam.
        """
        if mes in (12, 1, 7, 8):
            return "alta"
        if mes in (3, 4, 5, 6, 9):
            return "media"
        return "baja"

    def _ajuste_precio_por_temporada(self, temporada: str) -> float:
        """
        Devuelve un factor multiplicador para el precio según temporada.
        """
        if temporada == "alta":
            return 1.15 + random.uniform(0.0, 0.20)   # +15% a +35%
        if temporada == "baja":
            return 0.75 + random.uniform(0.0, 0.10)   # -25% a -15%
        # media
        return 0.95 + random.uniform(0.0, 0.10)       # -5% a +5%

    # ============================
    #  Helpers de fechas
    # ============================
    def _rango_fechas(self):
        """
        Devuelve (fecha_inicio, fecha_fin) desde MARZO del año actual hasta hoy.
        Si estamos antes de marzo, toma marzo del año anterior.
        """
        hoy = timezone.now().date()
        year = hoy.year
        if hoy.month < 3:
            year -= 1
        inicio = date(year, 3, 1)
        return inicio, hoy

    def _fecha_random_en_rango(self, inicio: date, fin: date) -> date:
        dias = (fin - inicio).days
        if dias <= 0:
            return inicio
        return inicio + timedelta(days=random.randint(0, dias))

    # ============================
    #  Helpers de perfiles
    # ============================
    def _elegir_perfil(self) -> str:
        """
        Devuelve 'corporativo' o 'turismo' según pesos.
        """
        return random.choices(
            ["corporativo", "turismo"],
            weights=[0.55, 0.45],
            k=1,
        )[0]

    def _elegir_estado_reserva(self) -> str:
        """
        Escoge estado de reserva con pesos.
        """
        return random.choices(
            [
                Reserva.REALIZADA,
                Reserva.CONFIRMADA,
                Reserva.PENDIENTE,
                Reserva.CANCELADA,
            ],
            weights=[0.6, 0.2, 0.15, 0.05],
            k=1,
        )[0]

    # ============================
    #  LÓGICA PRINCIPAL
    # ============================
    def handle(self, *args, **options):
        schema_arg = options.get("schema")
        num_reservas = options.get("reservas", 300)

        TenantModel = get_tenant_model()

        if schema_arg:
            tenants = TenantModel.objects.filter(schema_name=schema_arg)
            if not tenants.exists():
                self.stdout.write(
                    self.style.ERROR(f"No se encontró el tenant con schema '{schema_arg}'")
                )
                return
        else:
            # Obtener tenants REALES (no el public)
            tenants = TenantModel.objects.exclude(schema_name="public")

        if not tenants:
            self.stdout.write(self.style.ERROR("No hay tenants registrados en core_tenant"))
            return

        self.stdout.write(self.style.SUCCESS("===== INICIANDO SEEDER MASIVO MULTITENANT ====="))

        for tenant in tenants:
            self.stdout.write(
                self.style.WARNING(
                    f"\n>>> Procesando tenant: {tenant.schema_name} ({tenant.name})"
                )
            )

            # Saltar si por alguna razón aparece public
            if tenant.schema_name == "public":
                self.stdout.write(self.style.WARNING(">> Saltando tenant PUBLIC"))
                continue

            # Cambiar al schema del tenant
            connection.set_schema(tenant.schema_name, True)
            self._seed_tenant(tenant, num_reservas)

        # Volver a public por seguridad
        from django_tenants.utils import get_public_schema_name

        connection.set_schema(get_public_schema_name(), True)
        self.stdout.write(self.style.SUCCESS("\n===== SEEDER COMPLETO PARA TODOS LOS TENANTS ====="))

    def _seed_tenant(self, tenant, num_reservas: int):
        # -------------------------
        # 0. Hoteles del schema
        # -------------------------
        hoteles = list(Hotel.objects.all())
        if not hoteles:
            # Si no hay hoteles, creamos uno usando el nombre del tenant
            hotel = Hotel.objects.create(
                nombre=tenant.name or f"Hotel {tenant.schema_name}",
                telefono="70000000",
                direccion="Dirección demo",
                ciudad="Santa Cruz",
                pais="Bolivia",
                estado="Activo",
            )
            hoteles = [hotel]

        hotel_principal = hoteles[0]

        # -------------------------
        # 1. Usuarios (al menos 25, todos asignados al hotel_principal)
        # -------------------------
        usuarios = []
        for i in range(25):
            username = f"user{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@{tenant.schema_name}.test",
                    # Si usas create_user mejor, pero para seeder de prueba:
                    "is_active": True,
                },
            )
            # Asignar hotel si tu modelo tiene FK hotel
            if hasattr(user, "hotel") and not user.hotel_id:
                user.hotel = hotel_principal
                user.save()

            usuarios.append(user)

        self.stdout.write(self.style.SUCCESS(f"✔ {len(usuarios)} usuarios creados/asegurados"))

        # Escogemos ~30% como clientes recurrentes
        num_recurrentes = max(1, int(len(usuarios) * 0.3))
        usuarios_recurrentes = random.sample(usuarios, num_recurrentes)

        # -------------------------
        # 2. Fidelización
        # -------------------------
        prog, _ = ProgramaFidelizacion.objects.get_or_create(
            nombre="Fidelización Premium",
            defaults={
                "descripcion": "Acumula puntos por estancia.",
                "descuento_maximo": 50,
                "puntos_por_dolar_descuento": 10,
            },
        )

        for user in usuarios:
            CuentaFidelizacion.objects.get_or_create(
                cliente=user,
                fidelizacion=prog,
                defaults={
                    "puntos_acumulados": random.randint(
                        200, 1500
                    )
                    if user in usuarios_recurrentes
                    else random.randint(0, 300)
                },
            )

        self.stdout.write(self.style.SUCCESS("✔ Fidelización asignada"))

        # -------------------------
        # 3. Habitaciones
        # -------------------------
        # Distribución realista por tipo
        tipos = ["individual", "doble", "familiar", "suite", "deluxe"]
        pesos_tipos = [0.30, 0.25, 0.20, 0.15, 0.10]

        # Rangos de precios base (Bs por noche)
        rangos_precios = {
            "individual": (120, 180),
            "doble": (180, 260),
            "familiar": (450, 650),
            "suite": (300, 450),
            "deluxe": (400, 550),
        }

        habitaciones = []

        # Si ya hay habitaciones, las usamos; si no, creamos unas 20
        if Habitacion.objects.filter(hotel=hotel_principal).exists():
            habitaciones = list(Habitacion.objects.filter(hotel=hotel_principal))
        else:
            for i in range(20):
                tipo = random.choices(tipos, weights=pesos_tipos, k=1)[0]
                base_min, base_max = rangos_precios[tipo]
                precio = random.randint(base_min, base_max)

                hab = Habitacion.objects.create(
                    hotel=hotel_principal,
                    numero=str(100 + i),
                    capacidad=str(random.choice([1, 2, 3, 4])),
                    descripcion=f"Habitación tipo {tipo}",
                    precio_noche=precio,
                    estado=Habitacion.DISPONIBLE,
                    tamanio=f"{random.randint(25, 45)}m2",
                    tipo=tipo,
                )
                habitaciones.append(hab)

        self.stdout.write(
            self.style.SUCCESS(f"✔ {len(habitaciones)} habitaciones disponibles para {hotel_principal.nombre}")
        )

        # Agrupar por tipo para elegir según perfil
        hab_por_tipo = {}
        for hab in habitaciones:
            hab_por_tipo.setdefault(hab.tipo, []).append(hab)

        # -------------------------
        # 4. Servicios
        # -------------------------
        lista_servicios = [
            ("Spa", 50),
            ("Desayuno buffet", 25),
            ("Cena gourmet", 60),
            ("Lavandería", 15),
            ("Transporte aeropuerto", 40),
            ("Tours turísticos", 75),
            ("Bar", 35),
        ]

        servicios = []
        for nombre, precio in lista_servicios:
            s, _ = Servicio.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "descripcion": f"Servicio de {nombre.lower()}",
                    "precio": precio,
                    "tipo": "extra",
                },
            )
            servicios.append(s)

        self.stdout.write(self.style.SUCCESS(f"✔ {len(servicios)} servicios creados/asegurados"))

        # -------------------------
        # 5. Reservas + CheckInOut + Folios + ServiciosAsociados + Pagos
        # -------------------------
        fecha_inicio, fecha_fin = self._rango_fechas()

        reservas_creadas = 0

        for _ in range(num_reservas):
            perfil = self._elegir_perfil()

            # Elegir usuario (más probabilidad de usar recurrentes)
            if random.random() < 0.3:
                huesped = random.choice(usuarios_recurrentes)
            else:
                huesped = random.choice(usuarios)

            # Elegir habitación según perfil
            if perfil == "corporativo":
                # Prefiere individual / doble
                candidatos = (
                    hab_por_tipo.get("individual", [])
                    + hab_por_tipo.get("doble", [])
                )
            else:
                # turismo → familiar / suite / deluxe / doble
                candidatos = (
                    hab_por_tipo.get("familiar", [])
                    + hab_por_tipo.get("suite", [])
                    + hab_por_tipo.get("deluxe", [])
                    + hab_por_tipo.get("doble", [])
                )

            # Fallback si no hay candidatos
            if not candidatos:
                candidatos = habitaciones

            hab = random.choice(candidatos)

            # Fecha de entrada según perfil
            while True:
                entrada = self._fecha_random_en_rango(fecha_inicio, fecha_fin)
                wd = entrada.weekday()  # 0 Lunes - 6 Domingo
                if perfil == "corporativo" and wd < 5:  # L-V
                    break
                if perfil == "turismo" and wd >= 4:  # V-D
                    break

            # Noches
            if perfil == "corporativo":
                noches = random.randint(1, 3)
            else:
                noches = random.randint(2, 5)

            salida = entrada + timedelta(days=noches)

            # Temporada
            temporada = self._get_temporada(entrada.month)
            factor_precio = self._ajuste_precio_por_temporada(temporada)

            precio_noche_real = round(float(hab.precio_noche) * factor_precio, 2)
            total_reserva = precio_noche_real * noches

            # Fecha de reserva (1–60 días antes de la entrada)
            dias_anticipacion = random.randint(1, 60)
            fecha_reserva = entrada - timedelta(days=dias_anticipacion)

            estado = self._elegir_estado_reserva()

            reserva = Reserva.objects.create(
                fecha_reserva=fecha_reserva,
                fecha_entrada=entrada,
                fecha_salida=salida,
                total=total_reserva,
                estado=estado,
                habitacion=hab,
                huesped=huesped,
                hotel=hotel_principal,
            )

            # Check-in/out sólo si aplica
            if estado in [Reserva.REALIZADA, Reserva.CONFIRMADA, Reserva.PENDIENTE]:
                CheckInOut.objects.create(
                    reserva=reserva,
                    fecha_checkin=entrada,
                    hora_checkin=datetime.now().time(),
                    fecha_checkout=salida,
                    hora_checkout=datetime.now().time(),
                )

            # Folio de estancia
            if estado == Reserva.REALIZADA:
                total_pagado = total_reserva
                estado_folio = FolioEstancia.PAGADO
            else:
                total_pagado = 0
                estado_folio = FolioEstancia.PENDIENTE

            folio = FolioEstancia.objects.create(
                reserva=reserva,
                huesped=huesped,
                total_pagado=total_pagado,
                estado=estado_folio,
            )

            # Servicios asociados
            if perfil == "corporativo":
                num_servicios = random.randint(0, 2)
            else:
                num_servicios = random.randint(0, 4)

            for _ in range(num_servicios):
                servicio = random.choice(servicios)
                ServiciosAsociados.objects.create(
                    servicio=servicio,
                    reserva=reserva,
                    folioestancia=folio,
                    cantidad=random.randint(1, 3),
                    estado="completado",
                )

            # Pagos
            estado_pago = random.choice(
                [Pago.ESTADO_COMPLETADO, Pago.ESTADO_PENDIENTE]
            )

            Pago.objects.create(
                estado=estado_pago,
                metodo=random.choice(
                    ["tarjeta", "efectivo", "transferencia", "qr"]
                ),
                monto=total_pagado,
                referencia=f"PAY-{random.randint(10000, 99999)}",
                folio_estancia=folio,
            )

            reservas_creadas += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✔ {reservas_creadas} reservas generadas para tenant {tenant.schema_name}"
            )
        )
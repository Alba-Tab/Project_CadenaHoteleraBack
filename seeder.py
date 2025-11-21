"""
Seeder para poblar la base de datos con datos coherentes
Ejecutar: python seeder.py --schema nombre_schema
O para listar tenants: python seeder.py --list-tenants
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta, date
import random
import argparse

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import Group, Permission
from django_tenants.utils import schema_context, get_tenant_model
from core.models import Tenant
from apps.usuarios.models import User
from apps.hoteles.models import Hotel
from apps.habitaciones.models import Habitacion
from apps.servicios.models import Servicio
from apps.reservas.models import Reserva
from apps.checkinout.models import CheckInOut
from apps.folioestancias.models import FolioEstancia
from apps.servicios_asociados.models import ServiciosAsociados
from apps.pagos.models import Pago
from apps.fidelizacion.models import ProgramaFidelizacion, CuentaFidelizacion


# Lista de nombres y apellidos aleatorios
NOMBRES = [
    'Carlos', 'María', 'José', 'Ana', 'Luis', 'Carmen', 'Miguel', 'Isabel',
    'Francisco', 'Laura', 'Antonio', 'Rosa', 'Manuel', 'Teresa', 'Pedro',
    'Lucía', 'Javier', 'Elena', 'Rafael', 'Patricia', 'Diego', 'Marta',
    'Alejandro', 'Sofía', 'Daniel', 'Andrea', 'Fernando', 'Cristina',
    'Roberto', 'Beatriz', 'Alberto', 'Raquel', 'Jorge', 'Mónica', 'Sergio',
    'Natalia', 'Enrique', 'Paula', 'Ricardo', 'Verónica', 'Óscar', 'Sandra'
]

APELLIDOS = [
    'García', 'Rodríguez', 'Martínez', 'López', 'González', 'Pérez', 'Sánchez',
    'Ramírez', 'Torres', 'Flores', 'Rivera', 'Gómez', 'Díaz', 'Cruz', 'Morales',
    'Reyes', 'Ortiz', 'Gutiérrez', 'Chávez', 'Ruiz', 'Hernández', 'Jiménez',
    'Álvarez', 'Castillo', 'Romero', 'Herrera', 'Medina', 'Aguilar', 'Vargas',
    'Castro', 'Mendoza', 'Silva', 'Rojas', 'Vega', 'Moreno', 'Navarro'
]

TIPOS_HABITACION = ['individual', 'doble', 'suite']
CAPACIDADES = {'individual': '1', 'doble': '2', 'suite': '4'}
PRECIOS = {'individual': Decimal('80.00'), 'doble': Decimal('120.00'), 'suite': Decimal('250.00')}
TAMANIOS = {'individual': '20m²', 'doble': '35m²', 'suite': '60m²'}

SERVICIOS_DATA = [
    {'nombre': 'Desayuno Buffet', 'descripcion': 'Desayuno buffet completo', 'precio': Decimal('15.00'), 'tipo': 'Alimentación'},
    {'nombre': 'Almuerzo', 'descripcion': 'Almuerzo menú del día', 'precio': Decimal('25.00'), 'tipo': 'Alimentación'},
    {'nombre': 'Cena Gourmet', 'descripcion': 'Cena de 3 tiempos', 'precio': Decimal('35.00'), 'tipo': 'Alimentación'},
    {'nombre': 'Servicio de Habitación', 'descripcion': 'Room service 24h', 'precio': Decimal('10.00'), 'tipo': 'Servicio'},
    {'nombre': 'Lavandería Express', 'descripcion': 'Servicio de lavandería en el día', 'precio': Decimal('20.00'), 'tipo': 'Servicio'},
    {'nombre': 'Masaje Relajante', 'descripcion': 'Masaje de 60 minutos', 'precio': Decimal('50.00'), 'tipo': 'Spa'},
    {'nombre': 'Spa Completo', 'descripcion': 'Acceso a spa por día', 'precio': Decimal('40.00'), 'tipo': 'Spa'},
    {'nombre': 'Tour Ciudad', 'descripcion': 'Tour guiado por la ciudad', 'precio': Decimal('45.00'), 'tipo': 'Excursión'},
    {'nombre': 'Traslado Aeropuerto', 'descripcion': 'Transporte desde/hacia aeropuerto', 'precio': Decimal('30.00'), 'tipo': 'Transporte'},
    {'nombre': 'Renta de Auto', 'descripcion': 'Alquiler de vehículo por día', 'precio': Decimal('60.00'), 'tipo': 'Transporte'},
]

METODOS_PAGO = ['efectivo', 'tarjeta_credito', 'tarjeta_debito', 'transferencia']


def generar_nombre_completo():
    """Genera un nombre y apellido aleatorio"""
    nombre = random.choice(NOMBRES)
    apellido1 = random.choice(APELLIDOS)
    apellido2 = random.choice(APELLIDOS)
    return f"{nombre} {apellido1} {apellido2}", nombre.lower()


def crear_roles():
    """Crea los 3 roles: Admin, Recepcionista y Cliente"""
    print("Creando roles...")
    
    roles_data = [
        {'name': 'Admin', 'permissions': ['can_manage_hotels', 'can_manage_rooms', 'can_view_reports', 'can_manage_bookings', 'can_manage_users']},
        {'name': 'Recepcionista', 'permissions': ['can_manage_rooms', 'can_manage_bookings']},
        {'name': 'Cliente', 'permissions': []},
    ]
    
    roles = {}
    for role_data in roles_data:
        role, created = Group.objects.get_or_create(name=role_data['name'])
        if created:
            print(f"  ✓ Rol '{role_data['name']}' creado")
            # Asignar permisos
            for perm_codename in role_data['permissions']:
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    role.permissions.add(permission)
                except Permission.DoesNotExist:
                    print(f"    ! Permiso '{perm_codename}' no encontrado")
        else:
            print(f"  - Rol '{role_data['name']}' ya existe")
        roles[role_data['name']] = role
    
    return roles


def crear_hotel():
    """Crea un hotel principal"""
    print("\nCreando hotel...")
    
    hotel, created = Hotel.objects.get_or_create(
        nombre='Hotel Grand Palace',
        defaults={
            'telefono': '+1-555-0100',
            'direccion': 'Av. Principal 123',
            'ciudad': 'Ciudad de México',
            'pais': 'México',
            'estado': 'CDMX'
        }
    )
    
    if created:
        print(f"  ✓ Hotel '{hotel.nombre}' creado")
    else:
        print(f"  - Hotel '{hotel.nombre}' ya existe")
    
    return hotel


def crear_habitaciones(hotel, cantidad=25):
    """Crea habitaciones para el hotel"""
    print(f"\nCreando {cantidad} habitaciones...")
    
    habitaciones = []
    for i in range(1, cantidad + 1):
        tipo = random.choice(TIPOS_HABITACION)
        
        habitacion, created = Habitacion.objects.get_or_create(
            hotel=hotel,
            numero=f"{100 + i}",
            defaults={
                'capacidad': CAPACIDADES[tipo],
                'descripcion': f'Habitación {tipo} con vista panorámica',
                'precio_noche': PRECIOS[tipo],
                'estado': Habitacion.DISPONIBLE,
                'tamanio': TAMANIOS[tipo],
                'tipo': tipo
            }
        )
        
        if created:
            habitaciones.append(habitacion)
            if i % 10 == 0:
                print(f"  ✓ {i} habitaciones creadas...")
    
    print(f"  ✓ Total: {len(habitaciones)} habitaciones nuevas")
    return list(Habitacion.objects.filter(hotel=hotel))


def crear_servicios():
    """Crea los servicios disponibles"""
    print("\nCreando servicios...")
    
    servicios = []
    for serv_data in SERVICIOS_DATA:
        servicio, created = Servicio.objects.get_or_create(
            nombre=serv_data['nombre'],
            defaults={
                'descripcion': serv_data['descripcion'],
                'precio': serv_data['precio'],
                'tipo': serv_data['tipo']
            }
        )
        if created:
            servicios.append(servicio)
    
    print(f"  ✓ {len(servicios)} servicios nuevos creados")
    return list(Servicio.objects.all())


def crear_usuarios(roles, hotel, cantidad=40):
    """Crea usuarios con diferentes roles"""
    print(f"\nCreando {cantidad} usuarios...")
    
    # Obtener usuarios existentes
    usuarios_existentes = User.objects.count()
    print(f"  - Usuarios existentes: {usuarios_existentes}")
    
    # Distribución de roles: 2 admin, 5 recepcionistas, resto clientes
    usuarios = []
    
    # Crear admins (2)
    for i in range(2):
        nombre_completo, nombre = generar_nombre_completo()
        username = f"admin_{nombre}_{i+1}"
        
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f"{username}@hotel.com",
                password="12121212",
                first_name=nombre_completo.split()[0],
                last_name=' '.join(nombre_completo.split()[1:]),
                hotel=hotel
            )
            user.groups.add(roles['Admin'])
            usuarios.append(user)
    
    # Crear recepcionistas (5)
    for i in range(5):
        nombre_completo, nombre = generar_nombre_completo()
        username = f"recep_{nombre}_{i+1}"
        
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f"{username}@hotel.com",
                password="12121212",
                first_name=nombre_completo.split()[0],
                last_name=' '.join(nombre_completo.split()[1:]),
                hotel=hotel
            )
            user.groups.add(roles['Recepcionista'])
            usuarios.append(user)
    
    # Crear clientes (resto)
    clientes_a_crear = cantidad - 7  # 40 - 2 admin - 5 recepcionistas
    for i in range(clientes_a_crear):
        nombre_completo, nombre = generar_nombre_completo()
        username = f"cliente_{nombre}_{i+1}"
        
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password="12121212",
                first_name=nombre_completo.split()[0],
                last_name=' '.join(nombre_completo.split()[1:]),
                hotel=None  # Los clientes no están asociados al hotel inicialmente
            )
            user.groups.add(roles['Cliente'])
            usuarios.append(user)
    
    print(f"  ✓ {len(usuarios)} usuarios nuevos creados")
    print(f"  ✓ Total usuarios en sistema: {User.objects.count()}")
    
    return {
        'admins': list(User.objects.filter(groups__name='Admin')),
        'recepcionistas': list(User.objects.filter(groups__name='Recepcionista')),
        'clientes': list(User.objects.filter(groups__name='Cliente'))
    }


def crear_reservas(clientes, habitaciones, hotel, cantidad=30):
    """Crea reservas coherentes"""
    print(f"\nCreando {cantidad} reservas...")
    
    reservas = []
    fecha_inicio = date.today() - timedelta(days=60)
    
    for i in range(cantidad):
        cliente = random.choice(clientes)
        habitacion = random.choice(habitaciones)
        
        # Fechas aleatorias pero coherentes
        dias_desde_inicio = random.randint(0, 50)
        fecha_entrada = fecha_inicio + timedelta(days=dias_desde_inicio)
        noches = random.randint(1, 7)
        fecha_salida = fecha_entrada + timedelta(days=noches)
        
        # Calcular total
        total = habitacion.precio_noche * noches
        
        # Estado de la reserva
        if fecha_salida < date.today():
            estado = Reserva.REALIZADA
        elif fecha_entrada <= date.today() <= fecha_salida:
            estado = Reserva.CONFIRMADA
        else:
            estado = random.choice([Reserva.CONFIRMADA, Reserva.PENDIENTE])
        
        reserva = Reserva.objects.create(
            fecha_entrada=fecha_entrada,
            fecha_salida=fecha_salida,
            total=total,
            estado=estado,
            habitacion=habitacion,
            huesped=cliente,
            hotel=hotel
        )
        reservas.append(reserva)
        
        if (i + 1) % 10 == 0:
            print(f"  ✓ {i + 1} reservas creadas...")
    
    print(f"  ✓ Total: {len(reservas)} reservas creadas")
    return reservas


def crear_checkinout(reservas):
    """Crea check-ins y check-outs para reservas realizadas"""
    print("\nCreando check-ins y check-outs...")
    
    checkins = []
    for reserva in reservas:
        # Solo crear check-in para reservas confirmadas o realizadas
        if reserva.estado in [Reserva.CONFIRMADA, Reserva.REALIZADA]:
            # Si la fecha de entrada ya pasó
            if reserva.fecha_entrada <= date.today():
                
                # Check-in
                hora_checkin = datetime.strptime(f"{random.randint(14, 16)}:{random.randint(0, 59)}", "%H:%M").time()
                
                # Check-out (si ya pasó la fecha de salida)
                fecha_checkout = None
                hora_checkout = None
                if reserva.fecha_salida < date.today():
                    fecha_checkout = reserva.fecha_salida
                    hora_checkout = datetime.strptime(f"{random.randint(10, 12)}:{random.randint(0, 59)}", "%H:%M").time()
                
                checkinout, created = CheckInOut.objects.get_or_create(
                    reserva=reserva,
                    defaults={
                        'fecha_checkin': reserva.fecha_entrada,
                        'hora_checkin': hora_checkin,
                        'fecha_checkout': fecha_checkout,
                        'hora_checkout': hora_checkout,
                        'observaciones': 'Check-in realizado correctamente'
                    }
                )
                
                if created:
                    checkins.append(checkinout)
    
    print(f"  ✓ {len(checkins)} check-ins/outs creados")
    return checkins


def crear_folios_servicios_pagos(reservas, servicios):
    """Crea folios, servicios asociados y pagos"""
    print("\nCreando folios, servicios asociados y pagos...")
    
    folios = []
    servicios_asociados = []
    pagos_creados = []
    
    for reserva in reservas:
        # Crear folio solo para reservas con check-in
        if hasattr(reserva, 'checkinout'):
            # Determinar si ya finalizó la estancia
            if reserva.fecha_salida < date.today():
                estado_folio = FolioEstancia.PAGADO
            else:
                estado_folio = FolioEstancia.PENDIENTE
            
            folio = FolioEstancia.objects.create(
                estado=estado_folio,
                total_pagado=reserva.total,
                huesped=reserva.huesped,
                reserva=reserva
            )
            folios.append(folio)
            
            # Agregar servicios asociados (30% de probabilidad)
            if random.random() < 0.3:
                num_servicios = random.randint(1, 4)
                for _ in range(num_servicios):
                    servicio = random.choice(servicios)
                    cantidad = random.randint(1, 3)
                    
                    serv_asociado = ServiciosAsociados.objects.create(
                        servicio=servicio,
                        reserva=reserva,
                        folioestancia=folio,
                        cantidad=cantidad,
                        estado='completado' if estado_folio == FolioEstancia.PAGADO else 'confirmado'
                    )
                    servicios_asociados.append(serv_asociado)
            
            # Crear pago si el folio está pagado
            if estado_folio == FolioEstancia.PAGADO:
                total_general = folio.calcular_total_general()
                
                pago = Pago.objects.create(
                    estado=Pago.ESTADO_COMPLETADO,
                    metodo=random.choice(METODOS_PAGO),
                    monto=total_general,
                    referencia=f"REF-{random.randint(100000, 999999)}",
                    folio_estancia=folio
                )
                pagos_creados.append(pago)
                
                # Actualizar total_pagado del folio
                folio.total_pagado = total_general
                folio.save()
    
    print(f"  ✓ {len(folios)} folios creados")
    print(f"  ✓ {len(servicios_asociados)} servicios asociados")
    print(f"  ✓ {len(pagos_creados)} pagos completados")
    
    return folios, servicios_asociados, pagos_creados


def crear_programa_fidelizacion(clientes):
    """Crea programa de fidelización y cuentas para clientes"""
    print("\nCreando programa de fidelización...")
    
    # Crear programa
    programa, created = ProgramaFidelizacion.objects.get_or_create(
        nombre='Programa VIP Hotel Grand Palace',
        defaults={
            'descripcion': 'Acumula puntos por cada dólar gastado y obtén descuentos en tus próximas estadías',
            'descuento_maximo': 50,  # 50% máximo
            'activo': True,
            'puntos_por_dolar_descuento': 10  # 10 puntos = $1 descuento
        }
    )
    
    if created:
        print(f"  ✓ Programa '{programa.nombre}' creado")
    else:
        print(f"  - Programa '{programa.nombre}' ya existe")
    
    # Crear cuentas para clientes
    cuentas = []
    print("  Creando cuentas de fidelización para clientes...")
    
    for cliente in clientes:
        cuenta, created = CuentaFidelizacion.objects.get_or_create(
            cliente=cliente,
            fidelizacion=programa,
            defaults={
                'puntos_acumulados': random.randint(0, 500)  # Puntos iniciales aleatorios
            }
        )
        if created:
            cuentas.append(cuenta)
    
    print(f"  ✓ {len(cuentas)} cuentas de fidelización creadas")
    return programa, cuentas


def listar_tenants():
    """Lista todos los tenants disponibles"""
    print("=" * 60)
    print("TENANTS DISPONIBLES")
    print("=" * 60)
    
    tenants = Tenant.objects.all()
    
    if not tenants.exists():
        print("❌ No hay tenants creados en el sistema")
        print("\nPara crear un tenant, usa:")
        print("python manage.py create_tenant")
        return
    
    print(f"\nTotal de tenants: {tenants.count()}\n")
    
    for tenant in tenants:
        print(f"📦 Schema: {tenant.schema_name}")
        print(f"   Nombre: {tenant.name}")
        print(f"   En prueba: {'Sí' if tenant.on_trial else 'No'}")
        if tenant.paid_until:
            print(f"   Pagado hasta: {tenant.paid_until}")
        print()
    
    print("=" * 60)
    print("\nPara poblar un tenant específico, usa:")
    print("python seeder.py --schema nombre_del_schema")
    print("=" * 60)


def main():
    """Función principal que ejecuta el seeder con transacción"""
    # Parsear argumentos
    parser = argparse.ArgumentParser(description='Seeder para poblar la base de datos')
    parser.add_argument('--schema', type=str, help='Schema del tenant a poblar')
    parser.add_argument('--list-tenants', action='store_true', help='Lista todos los tenants disponibles')
    args = parser.parse_args()
    
    # Si se solicita listar tenants
    if args.list_tenants:
        listar_tenants()
        return
    
    # Validar que se especificó un schema
    if not args.schema:
        print("❌ ERROR: Debes especificar un schema con --schema")
        print("\nEjemplos de uso:")
        print("  python seeder.py --list-tenants          # Ver tenants disponibles")
        print("  python seeder.py --schema mi_hotel       # Poblar tenant específico")
        sys.exit(1)
    
    # Validar que el tenant existe
    try:
        tenant = Tenant.objects.get(schema_name=args.schema)
    except Tenant.DoesNotExist:
        print(f"❌ ERROR: El tenant con schema '{args.schema}' no existe")
        print("\nPara ver los tenants disponibles, ejecuta:")
        print("python seeder.py --list-tenants")
        sys.exit(1)
    
    print("=" * 60)
    print("INICIANDO SEEDER DE BASE DE DATOS")
    print("=" * 60)
    print(f"🎯 Tenant: {tenant.name}")
    print(f"🎯 Schema: {tenant.schema_name}")
    print("=" * 60)
    
    # Validar que el tenant tiene las tablas migradas
    print("\n⚙️  Verificando migraciones del tenant...")
    try:
        with schema_context(tenant.schema_name):
            # Intentar hacer una query simple para verificar que las tablas existen
            Hotel.objects.exists()
        print("✓ Tenant tiene las migraciones aplicadas\n")
    except Exception as e:
        print(f"\n❌ ERROR: El tenant '{args.schema}' no tiene las migraciones aplicadas")
        print(f"❌ Detalle: {str(e)}")
        print("\n📋 Para aplicar las migraciones a este tenant, ejecuta:")
        print(f"   python manage.py migrate_schemas --schema={args.schema}")
        print("\n💡 O para aplicar a todos los tenants:")
        print("   python manage.py migrate_schemas")
        print("=" * 60)
        sys.exit(1)
    
    try:
        # Usar schema_context para trabajar en el tenant específico
        with schema_context(tenant.schema_name):
            # Usar transacción atómica para rollback automático en caso de error
            with transaction.atomic():
                print("\n🔒 Iniciando transacción atómica...")
                
                # 1. Crear roles
                roles = crear_roles()
            
            # 2. Crear hotel
            hotel = crear_hotel()
            
            # 3. Crear habitaciones
            habitaciones = crear_habitaciones(hotel, cantidad=25)
            
            # 4. Crear servicios
            servicios = crear_servicios()
            
            # 5. Crear usuarios (40 usuarios: 2 admin, 5 recepcionistas, 33 clientes)
            usuarios = crear_usuarios(roles, hotel, cantidad=40)
            
            # 6. Crear reservas (30 reservas)
            reservas = crear_reservas(usuarios['clientes'], habitaciones, hotel, cantidad=30)
            
            # 7. Crear check-ins y check-outs
            checkinout = crear_checkinout(reservas)
            
            # 8. Crear folios, servicios asociados y pagos
            folios, servicios_asociados, pagos = crear_folios_servicios_pagos(reservas, servicios)
            
            # 9. Crear programa de fidelización
            programa, cuentas = crear_programa_fidelizacion(usuarios['clientes'])
            
            print("\n✓ Transacción completada, guardando cambios...")
            
            # Resumen final dentro del contexto del schema
            print("\n" + "=" * 60)
            print("RESUMEN FINAL")
            print("=" * 60)
            print(f"🎯 Tenant: {tenant.name} ({tenant.schema_name})")
            print(f"✓ Roles creados: 3 (Admin, Recepcionista, Cliente)")
            print(f"✓ Hoteles: {Hotel.objects.count()}")
            print(f"✓ Habitaciones: {Habitacion.objects.count()}")
            print(f"✓ Servicios: {Servicio.objects.count()}")
            print(f"✓ Usuarios totales: {User.objects.count()}")
            print(f"  - Admins: {len(usuarios['admins'])}")
            print(f"  - Recepcionistas: {len(usuarios['recepcionistas'])}")
            print(f"  - Clientes: {len(usuarios['clientes'])}")
            print(f"✓ Reservas: {Reserva.objects.count()}")
            print(f"✓ Check-ins/Outs: {CheckInOut.objects.count()}")
            print(f"✓ Folios: {FolioEstancia.objects.count()}")
            print(f"✓ Servicios asociados: {ServiciosAsociados.objects.count()}")
            print(f"✓ Pagos: {Pago.objects.count()}")
            print(f"✓ Programas fidelización: {ProgramaFidelizacion.objects.count()}")
            print(f"✓ Cuentas fidelización: {CuentaFidelizacion.objects.count()}")
            print("=" * 60)
            print("SEEDER COMPLETADO EXITOSAMENTE ✓")
            print("=" * 60)
            print("\nCredenciales de acceso:")
            print("  Contraseña para todos los usuarios: 12121212")
            print(f"  Ejemplo admin: admin_carlos_1 / 12121212")
            print(f"  Ejemplo recepcionista: recep_maria_1 / 12121212")
            print(f"  Ejemplo cliente: cliente_jose_1 / 12121212")
            print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR DETECTADO - REALIZANDO ROLLBACK")
        print(f"❌ Motivo: {str(e)}")
        print("❌ Todos los cambios han sido revertidos")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

"""
Seeder de Reservas con Timeline Realista
Crea reservas distribuidas en el tiempo con su flujo completo:
Reserva -> CheckIn -> Servicios -> CheckOut -> Folio -> Pago

Ejecutar: python seeder_reservas_timeline.py --schema nombre_schema --reservas 50
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta, date, time
import random
import argparse

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from django_tenants.utils import schema_context
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
from apps.fidelizacion.models import CuentaFidelizacion


METODOS_PAGO = ['efectivo', 'tarjeta_credito', 'tarjeta_debito', 'transferencia']


def distribuir_fechas_timeline(cantidad_reservas, dias_atras=90, dias_adelante=30):
    """
    Genera fechas de reserva distribuidas de forma realista
    - Pasado: reservas ya finalizadas (check-out realizado)
    - Presente: reservas activas (check-in hecho, esperando check-out)
    - Futuro: reservas confirmadas (aún no inician)
    """
    hoy = date.today()
    inicio_timeline = hoy - timedelta(days=dias_atras)
    fin_timeline = hoy + timedelta(days=dias_adelante)
    
    fechas_reservas = []
    
    # Distribuir reservas en el timeline
    for i in range(cantidad_reservas):
        # Calcular fecha de entrada aleatoria en el rango
        dias_desde_inicio = random.randint(0, dias_atras + dias_adelante)
        fecha_entrada = inicio_timeline + timedelta(days=dias_desde_inicio)
        
        # Duración de estancia (más realista)
        # 70% estadías cortas (1-3 noches)
        # 20% estadías medias (4-7 noches)
        # 10% estadías largas (8-14 noches)
        rand = random.random()
        if rand < 0.70:
            noches = random.randint(1, 3)
        elif rand < 0.90:
            noches = random.randint(4, 7)
        else:
            noches = random.randint(8, 14)
        
        fecha_salida = fecha_entrada + timedelta(days=noches)
        
        # Determinar estado según la línea de tiempo
        if fecha_salida < hoy:
            estado = 'finalizada'  # Ya terminó
            tipo = 'pasado'
        elif fecha_entrada <= hoy < fecha_salida:
            estado = 'activa'  # En curso
            tipo = 'presente'
        elif fecha_entrada > hoy:
            # Reservas futuras pueden estar confirmadas o pendientes
            estado = random.choice(['confirmada', 'confirmada', 'pendiente'])
            tipo = 'futuro'
        else:
            estado = 'confirmada'
            tipo = 'presente'
        
        fechas_reservas.append({
            'fecha_entrada': fecha_entrada,
            'fecha_salida': fecha_salida,
            'noches': noches,
            'estado': estado,
            'tipo': tipo
        })
    
    # Ordenar por fecha de entrada para simular el orden cronológico
    fechas_reservas.sort(key=lambda x: x['fecha_entrada'])
    
    return fechas_reservas


def crear_reserva_completa(cliente, habitacion, hotel, fecha_info, servicios_disponibles):
    """
    Crea una reserva completa con todo su ciclo:
    1. Reserva
    2. Check-in (si ya pasó la fecha de entrada)
    3. Servicios asociados (durante la estancia)
    4. Check-out (si ya pasó la fecha de salida)
    5. Folio
    6. Pago (si ya hizo check-out)
    """
    # 1. CREAR RESERVA
    total_habitacion = habitacion.precio_noche * fecha_info['noches']
    
    # Mapear estados a los del modelo
    if fecha_info['estado'] == 'finalizada':
        estado_reserva = Reserva.REALIZADA
    elif fecha_info['estado'] == 'activa':
        estado_reserva = Reserva.CONFIRMADA
    elif fecha_info['estado'] == 'confirmada':
        estado_reserva = Reserva.CONFIRMADA
    else:
        estado_reserva = Reserva.PENDIENTE
    
    reserva = Reserva.objects.create(
        fecha_entrada=fecha_info['fecha_entrada'],
        fecha_salida=fecha_info['fecha_salida'],
        total=total_habitacion,
        estado=estado_reserva,
        habitacion=habitacion,
        huesped=cliente,
        hotel=hotel
    )
    
    resultado = {
        'reserva': reserva,
        'checkin': None,
        'servicios': [],
        'folio': None,
        'pago': None,
        'tipo': fecha_info['tipo']
    }
    
    # 2. CHECK-IN (si la fecha de entrada ya pasó)
    if fecha_info['fecha_entrada'] <= date.today():
        hora_checkin = time(
            hour=random.randint(14, 17),
            minute=random.randint(0, 59)
        )
        
        # Check-out (si la fecha de salida ya pasó)
        fecha_checkout = None
        hora_checkout = None
        if fecha_info['fecha_salida'] < date.today():
            fecha_checkout = fecha_info['fecha_salida']
            hora_checkout = time(
                hour=random.randint(10, 12),
                minute=random.randint(0, 59)
            )
        
        checkinout = CheckInOut.objects.create(
            reserva=reserva,
            fecha_checkin=fecha_info['fecha_entrada'],
            hora_checkin=hora_checkin,
            fecha_checkout=fecha_checkout,
            hora_checkout=hora_checkout,
            observaciones='Check-in realizado' if not fecha_checkout else 'Estancia finalizada'
        )
        resultado['checkin'] = checkinout
        
        # 3. CREAR FOLIO (una vez que hay check-in)
        estado_folio = FolioEstancia.PAGADO if fecha_info['fecha_salida'] < date.today() else FolioEstancia.PENDIENTE
        
        folio = FolioEstancia.objects.create(
            estado=estado_folio,
            total_pagado=total_habitacion,
            huesped=cliente,
            reserva=reserva
        )
        resultado['folio'] = folio
        
        # 4. SERVICIOS ASOCIADOS (50% de probabilidad si hay check-in)
        if random.random() < 0.5 and servicios_disponibles:
            num_servicios = random.randint(1, 3)
            for _ in range(num_servicios):
                servicio = random.choice(servicios_disponibles)
                cantidad = random.randint(1, 2)
                
                # Estado del servicio según el estado de la estancia
                if fecha_info['fecha_salida'] < date.today():
                    estado_servicio = 'completado'
                elif fecha_info['fecha_entrada'] <= date.today():
                    estado_servicio = random.choice(['confirmado', 'en_proceso', 'completado'])
                else:
                    estado_servicio = 'solicitado'
                
                serv_asociado = ServiciosAsociados.objects.create(
                    servicio=servicio,
                    reserva=reserva,
                    folioestancia=folio,
                    cantidad=cantidad,
                    estado=estado_servicio,
                    observaciones=f'{servicio.nombre} - {cantidad}x'
                )
                resultado['servicios'].append(serv_asociado)
        
        # 5. PAGO (si ya hizo check-out)
        if fecha_info['fecha_salida'] < date.today():
            # Calcular total general (habitación + servicios)
            total_general = folio.calcular_total_general()
            
            pago = Pago.objects.create(
                estado=Pago.ESTADO_COMPLETADO,
                metodo=random.choice(METODOS_PAGO),
                monto=total_general,
                referencia=f"PAY-{random.randint(100000, 999999)}",
                folio_estancia=folio
            )
            resultado['pago'] = pago
            
            # Actualizar folio con total pagado
            folio.total_pagado = total_general
            folio.save()
            
            # Acumular puntos de fidelización
            try:
                cuenta_fidelizacion = CuentaFidelizacion.objects.get(cliente=cliente)
                cuenta_fidelizacion.acumular_puntos(float(total_general))
            except CuentaFidelizacion.DoesNotExist:
                pass  # Cliente no tiene cuenta de fidelización
    
    return resultado


def generar_reservas_timeline(schema_name, cantidad_reservas):
    """Genera reservas distribuidas en una línea de tiempo realista"""
    
    print("=" * 70)
    print("GENERADOR DE RESERVAS CON TIMELINE REALISTA")
    print("=" * 70)
    print(f"🎯 Schema: {schema_name}")
    print(f"🎯 Cantidad de reservas: {cantidad_reservas}")
    print("=" * 70)
    
    try:
        with schema_context(schema_name):
            # Verificar que existen datos base
            clientes = list(User.objects.filter(groups__name='Cliente'))
            habitaciones = list(Habitacion.objects.all())
            servicios = list(Servicio.objects.all())
            
            if not clientes:
                print("❌ ERROR: No hay clientes en el sistema. Ejecuta el seeder principal primero.")
                return
            
            if not habitaciones:
                print("❌ ERROR: No hay habitaciones en el sistema. Ejecuta el seeder principal primero.")
                return
            
            hotel = Hotel.objects.first()
            if not hotel:
                print("❌ ERROR: No hay hoteles en el sistema. Ejecuta el seeder principal primero.")
                return
            
            print(f"\n📊 Datos disponibles:")
            print(f"   • Clientes: {len(clientes)}")
            print(f"   • Habitaciones: {len(habitaciones)}")
            print(f"   • Servicios: {len(servicios)}")
            print(f"   • Hotel: {hotel.nombre}")
            
            # Generar distribución temporal
            print(f"\n⏰ Generando timeline de reservas...")
            fechas_timeline = distribuir_fechas_timeline(cantidad_reservas)
            
            # Contar por tipo
            pasadas = sum(1 for f in fechas_timeline if f['tipo'] == 'pasado')
            activas = sum(1 for f in fechas_timeline if f['tipo'] == 'presente')
            futuras = sum(1 for f in fechas_timeline if f['tipo'] == 'futuro')
            
            print(f"\n📅 Distribución temporal:")
            print(f"   • Reservas pasadas (finalizadas): {pasadas}")
            print(f"   • Reservas activas (en curso): {activas}")
            print(f"   • Reservas futuras (confirmadas): {futuras}")
            
            # Crear reservas con transacción
            print(f"\n🔒 Iniciando creación de reservas...")
            
            with transaction.atomic():
                resultados = {
                    'pasado': {'reservas': 0, 'checkins': 0, 'checkouts': 0, 'servicios': 0, 'pagos': 0},
                    'presente': {'reservas': 0, 'checkins': 0, 'checkouts': 0, 'servicios': 0, 'pagos': 0},
                    'futuro': {'reservas': 0, 'checkins': 0, 'checkouts': 0, 'servicios': 0, 'pagos': 0},
                }
                
                for i, fecha_info in enumerate(fechas_timeline, 1):
                    # Seleccionar cliente y habitación aleatoriamente
                    cliente = random.choice(clientes)
                    habitacion = random.choice(habitaciones)
                    
                    # Crear reserva completa con su ciclo
                    resultado = crear_reserva_completa(
                        cliente, habitacion, hotel, fecha_info, servicios
                    )
                    
                    # Actualizar contadores
                    tipo = resultado['tipo']
                    resultados[tipo]['reservas'] += 1
                    if resultado['checkin']:
                        resultados[tipo]['checkins'] += 1
                        if resultado['checkin'].fecha_checkout:
                            resultados[tipo]['checkouts'] += 1
                    if resultado['servicios']:
                        resultados[tipo]['servicios'] += len(resultado['servicios'])
                    if resultado['pago']:
                        resultados[tipo]['pagos'] += 1
                    
                    # Mostrar progreso cada 10 reservas
                    if i % 10 == 0:
                        print(f"   ✓ {i}/{cantidad_reservas} reservas procesadas...")
                
                print(f"   ✓ {cantidad_reservas}/{cantidad_reservas} reservas procesadas...")
                print("\n✅ Todas las reservas creadas exitosamente")
            
            # RESUMEN FINAL
            print("\n" + "=" * 70)
            print("RESUMEN DETALLADO POR PERIODO")
            print("=" * 70)
            
            print("\n📊 RESERVAS PASADAS (Finalizadas):")
            print(f"   • Reservas creadas: {resultados['pasado']['reservas']}")
            print(f"   • Check-ins realizados: {resultados['pasado']['checkins']}")
            print(f"   • Check-outs realizados: {resultados['pasado']['checkouts']}")
            print(f"   • Servicios contratados: {resultados['pasado']['servicios']}")
            print(f"   • Pagos completados: {resultados['pasado']['pagos']}")
            
            print("\n📊 RESERVAS ACTIVAS (En curso):")
            print(f"   • Reservas creadas: {resultados['presente']['reservas']}")
            print(f"   • Check-ins realizados: {resultados['presente']['checkins']}")
            print(f"   • Check-outs realizados: {resultados['presente']['checkouts']}")
            print(f"   • Servicios contratados: {resultados['presente']['servicios']}")
            print(f"   • Pagos completados: {resultados['presente']['pagos']}")
            
            print("\n📊 RESERVAS FUTURAS (Confirmadas):")
            print(f"   • Reservas creadas: {resultados['futuro']['reservas']}")
            print(f"   • Check-ins realizados: {resultados['futuro']['checkins']}")
            print(f"   • Servicios contratados: {resultados['futuro']['servicios']}")
            
            # Totales generales
            with schema_context(schema_name):
                print("\n" + "=" * 70)
                print("TOTALES GENERALES EN EL SISTEMA")
                print("=" * 70)
                print(f"✓ Total Reservas: {Reserva.objects.count()}")
                print(f"✓ Total Check-ins/Outs: {CheckInOut.objects.count()}")
                print(f"✓ Total Folios: {FolioEstancia.objects.count()}")
                print(f"✓ Total Servicios Asociados: {ServiciosAsociados.objects.count()}")
                print(f"✓ Total Pagos: {Pago.objects.count()}")
                print("=" * 70)
                
                print("\n💡 FLUJO DEL SISTEMA:")
                print("   1️⃣  Cliente hace RESERVA (cualquier momento)")
                print("   2️⃣  En fecha entrada: CHECK-IN + se crea FOLIO")
                print("   3️⃣  Durante estancia: Cliente puede solicitar SERVICIOS")
                print("   4️⃣  En fecha salida: CHECK-OUT")
                print("   5️⃣  Después check-out: PAGO completa el folio")
                print("   6️⃣  Sistema acumula PUNTOS de fidelización")
                print("=" * 70)
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Generador de reservas con timeline realista'
    )
    parser.add_argument(
        '--schema',
        type=str,
        required=True,
        help='Schema del tenant'
    )
    parser.add_argument(
        '--reservas',
        type=int,
        default=50,
        help='Cantidad de reservas a generar (default: 50)'
    )
    
    args = parser.parse_args()
    
    # Validar tenant
    try:
        tenant = Tenant.objects.get(schema_name=args.schema)
    except Tenant.DoesNotExist:
        print(f"❌ ERROR: El tenant '{args.schema}' no existe")
        sys.exit(1)
    
    # Generar reservas
    generar_reservas_timeline(args.schema, args.reservas)
    
    print("\n✅ PROCESO COMPLETADO EXITOSAMENTE")


if __name__ == '__main__':
    main()

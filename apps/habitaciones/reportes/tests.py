"""
Tests para el módulo de reportes de habitaciones con porcentaje de ocupación
"""
from datetime import date, timedelta
from django.test import TestCase
from apps.habitaciones.models import Habitacion
from apps.reservas.models import Reserva
from apps.hoteles.models import Hotel
from apps.usuarios.models import User
from apps.habitaciones.reportes.servicios import (
    calcular_porcentaje_ocupacion,
    agregar_porcentaje_ocupacion_a_rows
)


class PorcentajeOcupacionTestCase(TestCase):
    """Tests para el cálculo del porcentaje de ocupación"""

    def setUp(self):
        """Configuración inicial de los tests"""
        # Crear usuario de prueba
        self.usuario = User.objects.create_user(
            username='test_user',
            email='test@test.com',
            password='test123'
        )

        # Crear hotel de prueba
        self.hotel = Hotel.objects.create(
            nombre='Hotel Test',
            direccion='Calle Test 123',
            telefono='123456789',
            email='hotel@test.com'
        )

        # Crear habitación de prueba
        self.habitacion = Habitacion.objects.create(
            hotel=self.hotel,
            numero='101',
            capacidad='2',
            descripcion='Habitación de prueba',
            precio_noche=100.00,
            estado=Habitacion.DISPONIBLE,
            tamanio='25',
            tipo='doble'
        )

    def test_sin_reservas(self):
        """Test cuando no hay reservas"""
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=30)

        porcentaje = calcular_porcentaje_ocupacion(
            self.habitacion.id,
            fecha_inicio,
            fecha_fin
        )

        self.assertEqual(porcentaje, 0.0)

    def test_una_reserva_completa(self):
        """Test con una reserva que cubre todo el período"""
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=9)  # 10 días

        # Crear reserva que cubre todo el período
        Reserva.objects.create(
            habitacion=self.habitacion,
            huesped=self.usuario,
            hotel=self.hotel,
            fecha_entrada=fecha_inicio,
            fecha_salida=fecha_fin,
            total=1000.00,
            estado=Reserva.CONFIRMADA
        )

        porcentaje = calcular_porcentaje_ocupacion(
            self.habitacion.id,
            fecha_inicio,
            fecha_fin
        )

        # Debería ser 100% porque la reserva cubre todo el período
        self.assertEqual(porcentaje, 100.0)

    def test_reserva_parcial(self):
        """Test con una reserva que cubre parte del período"""
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=9)  # 10 días

        # Crear reserva de 5 días (50% del período)
        Reserva.objects.create(
            habitacion=self.habitacion,
            huesped=self.usuario,
            hotel=self.hotel,
            fecha_entrada=fecha_inicio,
            fecha_salida=fecha_inicio + timedelta(days=4),  # 5 días
            total=500.00,
            estado=Reserva.CONFIRMADA
        )

        porcentaje = calcular_porcentaje_ocupacion(
            self.habitacion.id,
            fecha_inicio,
            fecha_fin
        )

        # Debería ser 50%
        self.assertEqual(porcentaje, 50.0)

    def test_reserva_cancelada_no_cuenta(self):
        """Test que las reservas canceladas no cuentan para el porcentaje"""
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=9)  # 10 días

        # Crear reserva cancelada
        Reserva.objects.create(
            habitacion=self.habitacion,
            huesped=self.usuario,
            hotel=self.hotel,
            fecha_entrada=fecha_inicio,
            fecha_salida=fecha_fin,
            total=1000.00,
            estado=Reserva.CANCELADA
        )

        porcentaje = calcular_porcentaje_ocupacion(
            self.habitacion.id,
            fecha_inicio,
            fecha_fin
        )

        # Debería ser 0% porque la reserva está cancelada
        self.assertEqual(porcentaje, 0.0)

    def test_multiples_reservas(self):
        """Test con múltiples reservas"""
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=29)  # 30 días

        # Crear 3 reservas de 5 días cada una (15 días total = 50%)
        for i in range(3):
            inicio = fecha_inicio + timedelta(days=i*10)
            Reserva.objects.create(
                habitacion=self.habitacion,
                huesped=self.usuario,
                hotel=self.hotel,
                fecha_entrada=inicio,
                fecha_salida=inicio + timedelta(days=4),  # 5 días
                total=500.00,
                estado=Reserva.CONFIRMADA
            )

        porcentaje = calcular_porcentaje_ocupacion(
            self.habitacion.id,
            fecha_inicio,
            fecha_fin
        )

        # 15 días de 30 = 50%
        self.assertEqual(porcentaje, 50.0)

    def test_agregar_porcentaje_a_rows(self):
        """Test de la función que añade el porcentaje a las filas"""
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=9)  # 10 días

        # Crear reserva
        Reserva.objects.create(
            habitacion=self.habitacion,
            huesped=self.usuario,
            hotel=self.hotel,
            fecha_entrada=fecha_inicio,
            fecha_salida=fecha_inicio + timedelta(days=4),  # 5 días
            total=500.00,
            estado=Reserva.CONFIRMADA
        )

        # Simular filas de reporte
        rows = [
            {
                'id': self.habitacion.id,
                'hotel__nombre': 'Hotel Test',
                'numero': '101',
                'estado': 'disponible'
            }
        ]

        # Añadir porcentaje de ocupación
        rows_con_porcentaje = agregar_porcentaje_ocupacion_a_rows(
            rows,
            fecha_inicio,
            fecha_fin
        )

        # Verificar que se añadió la columna
        self.assertIn('porcentaje_ocupacion', rows_con_porcentaje[0])
        self.assertEqual(rows_con_porcentaje[0]['porcentaje_ocupacion'], 50.0)

    def test_reserva_fuera_del_periodo(self):
        """Test con reserva fuera del período de análisis"""
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=9)  # 10 días

        # Crear reserva ANTES del período
        Reserva.objects.create(
            habitacion=self.habitacion,
            huesped=self.usuario,
            hotel=self.hotel,
            fecha_entrada=fecha_inicio - timedelta(days=20),
            fecha_salida=fecha_inicio - timedelta(days=15),
            total=500.00,
            estado=Reserva.CONFIRMADA
        )

        porcentaje = calcular_porcentaje_ocupacion(
            self.habitacion.id,
            fecha_inicio,
            fecha_fin
        )

        # Debería ser 0% porque la reserva está fuera del período
        self.assertEqual(porcentaje, 0.0)

    def test_reserva_solapamiento_parcial(self):
        """Test con reserva que solapa parcialmente con el período"""
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=9)  # 10 días

        # Crear reserva que empieza 3 días antes del período y termina 5 días después del inicio
        Reserva.objects.create(
            habitacion=self.habitacion,
            huesped=self.usuario,
            hotel=self.hotel,
            fecha_entrada=fecha_inicio - timedelta(days=3),
            fecha_salida=fecha_inicio + timedelta(days=4),  # 5 días dentro del período
            total=500.00,
            estado=Reserva.CONFIRMADA
        )

        porcentaje = calcular_porcentaje_ocupacion(
            self.habitacion.id,
            fecha_inicio,
            fecha_fin
        )

        # Debería contar solo los 5 días dentro del período = 50%
        self.assertEqual(porcentaje, 50.0)


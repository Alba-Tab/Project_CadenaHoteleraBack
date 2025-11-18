"""
Módulo de Machine Learning para recomendación de precios
Usa regresión lineal con scikit-learn y reglas heurísticas como fallback
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from apps.reservas.models import Reserva
from apps.habitaciones.models import Habitacion


class ModeloRecomendacionPrecios:
    """
    Modelo de Machine Learning para recomendar precios de habitaciones
    """
    
    def __init__(self):
        self.modelo = None
        self.r2_score = 0
        self.min_datos_ml = 50  # Mínimo de reservas para usar ML
    
    def obtener_datos_historicos(self, tipo_habitacion, meses=12):
        """
        Obtiene datos históricos de reservas para un tipo de habitación
        
        Args:
            tipo_habitacion: Tipo de habitación ('individual', 'doble', 'suite')
            meses: Número de meses atrás a considerar
        
        Returns:
            DataFrame con datos históricos
        """
        fecha_inicio = datetime.now() - timedelta(days=meses * 30)
        
        # Obtener reservas confirmadas/realizadas del tipo de habitación
        reservas = Reserva.objects.filter(
            habitacion__tipo=tipo_habitacion,
            estado__in=[Reserva.CONFIRMADA, Reserva.REALIZADA],
            fecha_reserva__gte=fecha_inicio
        ).select_related('habitacion')
        
        if not reservas.exists():
            return pd.DataFrame()
        
        # Construir dataset
        datos = []
        for reserva in reservas:
            duracion = (reserva.fecha_salida - reserva.fecha_entrada).days
            if duracion <= 0:
                continue
            
            precio_por_noche = float(reserva.total) / duracion
            
            datos.append({
                'mes': reserva.fecha_entrada.month,
                'temporada': self._calcular_temporada(reserva.fecha_entrada.month),
                'dias_anticipacion': (reserva.fecha_entrada - reserva.fecha_reserva).days,
                'duracion_estancia': duracion,
                'dia_semana': reserva.fecha_entrada.weekday(),
                'precio': precio_por_noche
            })
        
        return pd.DataFrame(datos)
    
    def _calcular_temporada(self, mes):
        """
        Calcula la temporada basada en el mes
        
        Returns:
            0: Baja, 1: Media, 2: Alta
        """
        TEMPORADA_ALTA = [12, 1, 7, 8]  # Dic, Ene, Jul, Ago
        TEMPORADA_MEDIA = [3, 4, 5, 6, 9]  # Mar-Jun, Sep
        TEMPORADA_BAJA = [2, 10, 11]  # Feb, Oct, Nov
        
        if mes in TEMPORADA_ALTA:
            return 2
        elif mes in TEMPORADA_MEDIA:
            return 1
        else:
            return 0
    
    def _detectar_evento_especial(self, fecha):
        """
        Detecta si una fecha está en un evento especial
        
        Returns:
            1 si es evento especial, 0 si no
        """
        mes = fecha.month
        dia = fecha.day
        
        # Navidad y Año Nuevo
        if (mes == 12 and dia >= 20) or (mes == 1 and dia <= 7):
            return 1
        
        # Carnaval (aproximado: febrero)
        if mes == 2 and 10 <= dia <= 15:
            return 1
        
        # Semana Santa (aproximado: marzo-abril)
        if mes in [3, 4] and 20 <= dia <= 28:
            return 1
        
        # Fiestas Patrias Bolivia
        if mes == 8 and dia in [6, 7]:
            return 1
        
        return 0
    
    def entrenar_modelo(self, tipo_habitacion):
        """
        Entrena el modelo de regresión lineal con datos históricos
        
        Args:
            tipo_habitacion: Tipo de habitación
        
        Returns:
            tuple: (exito: bool, mensaje: str, confianza: float)
        """
        df = self.obtener_datos_historicos(tipo_habitacion)
        
        if df.empty or len(df) < self.min_datos_ml:
            return False, f'Datos insuficientes ({len(df)} registros). Se usarán reglas heurísticas.', 0
        
        # Preparar datos
        X = df[['mes', 'temporada', 'dias_anticipacion', 'duracion_estancia', 'dia_semana']]
        y = df['precio']
        
        # Dividir en train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Entrenar modelo
        self.modelo = LinearRegression()
        self.modelo.fit(X_train, y_train)
        
        # Calcular confianza (R²)
        self.r2_score = self.modelo.score(X_test, y_test)
        confianza = max(0, min(100, self.r2_score * 100))
        
        return True, f'Modelo entrenado con {len(df)} datos', confianza
    
    def predecir_precio(self, tipo_habitacion, fecha_objetivo=None):
        """
        Predice el precio para un tipo de habitación en una fecha
        
        Args:
            tipo_habitacion: Tipo de habitación
            fecha_objetivo: Fecha para la cual predecir (default: hoy)
        
        Returns:
            tuple: (precio: Decimal, confianza: float, motivo: str)
        """
        if fecha_objetivo is None:
            fecha_objetivo = datetime.now()
        
        # Entrenar modelo si no existe
        if self.modelo is None:
            exito, mensaje, confianza_entrenamiento = self.entrenar_modelo(tipo_habitacion)
            
            if not exito:
                # Usar reglas heurísticas
                return self._precio_heuristico(tipo_habitacion, fecha_objetivo)
        
        # Preparar features para predicción
        mes = fecha_objetivo.month
        temporada = self._calcular_temporada(mes)
        dias_anticipacion = 30  # Promedio
        duracion_estancia = 2  # Promedio
        dia_semana = fecha_objetivo.weekday()
        
        X_pred = np.array([[mes, temporada, dias_anticipacion, duracion_estancia, dia_semana]])
        
        # Predecir
        precio_pred = self.modelo.predict(X_pred)[0]
        precio_pred = max(50, precio_pred)  # Precio mínimo
        
        confianza = self.r2_score * 100
        motivo = self._generar_motivo(temporada, fecha_objetivo)
        
        return Decimal(str(round(precio_pred, 2))), confianza, motivo
    
    def _precio_heuristico(self, tipo_habitacion, fecha):
        """
        Calcula precio usando reglas heurísticas (cuando no hay suficientes datos)
        
        Returns:
            tuple: (precio: Decimal, confianza: float, motivo: str)
        """
        # Obtener precio base actual
        habitacion = Habitacion.objects.filter(tipo=tipo_habitacion).first()
        if not habitacion:
            return Decimal('100.00'), 50.0, 'Precio base por defecto'
        
        precio_base = float(habitacion.precio_noche)
        
        # Calcular ajustes
        temporada = self._calcular_temporada(fecha.month)
        evento_especial = self._detectar_evento_especial(fecha)
        
        # Aplicar reglas
        if temporada == 2:  # Alta
            ajuste = 1.25  # +25%
            motivo = 'Temporada alta'
        elif temporada == 1:  # Media
            ajuste = 1.0
            motivo = 'Temporada media'
        else:  # Baja
            ajuste = 0.85  # -15%
            motivo = 'Temporada baja'
        
        if evento_especial:
            ajuste *= 1.15  # +15% adicional por evento
            motivo += ' + Evento especial'
        
        precio_final = precio_base * ajuste
        confianza = 70.0  # Confianza moderada para reglas heurísticas
        
        return Decimal(str(round(precio_final, 2))), confianza, motivo
    
    def _generar_motivo(self, temporada, fecha):
        """
        Genera el motivo de la recomendación
        """
        motivos = []
        
        if temporada == 2:
            motivos.append('Temporada alta detectada')
        elif temporada == 0:
            motivos.append('Temporada baja detectada')
        
        if self._detectar_evento_especial(fecha):
            motivos.append('Evento especial próximo')
        
        if not motivos:
            motivos.append('Análisis de datos históricos')
        
        return ' | '.join(motivos)
    
    def calcular_ocupacion_hotel(self, hotel_id, fecha=None):
        """
        Calcula el porcentaje de ocupación actual del hotel
        
        Args:
            hotel_id: ID del hotel
            fecha: Fecha para calcular ocupación (default: hoy)
        
        Returns:
            float: Porcentaje de ocupación (0-100)
        """
        if fecha is None:
            fecha = datetime.now().date()
        
        total_habitaciones = Habitacion.objects.filter(hotel_id=hotel_id).count()
        if total_habitaciones == 0:
            return 0
        
        # Contar habitaciones ocupadas en la fecha
        habitaciones_ocupadas = Reserva.objects.filter(
            hotel_id=hotel_id,
            estado__in=[Reserva.CONFIRMADA, Reserva.REALIZADA],
            fecha_entrada__lte=fecha,
            fecha_salida__gte=fecha
        ).count()
        
        ocupacion = (habitaciones_ocupadas / total_habitaciones) * 100
        return round(ocupacion, 2)

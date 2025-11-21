import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from joblib import dump, load
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

from apps.reservas.models import Reserva
from apps.habitaciones.models import Habitacion


class ModeloRecomendacionPrecios:

    def __init__(self):
        self.modelo = None
        self.r2_score = 0
        self.min_datos_ml = 40
        self.path_modelos = "ml_models"  # Carpeta donde se guardan los modelos

        if not os.path.exists(self.path_modelos):
            os.makedirs(self.path_modelos)

    # ---------------------------------------------------------------
    # 1) Construcción del Dataset
    # ---------------------------------------------------------------
    def obtener_datos_historicos(self, hotel_id, tipo_habitacion, meses=12):
        fecha_inicio = datetime.now() - timedelta(days=meses * 30)

        reservas = Reserva.objects.filter(
            habitacion__tipo=tipo_habitacion,
            hotel_id=hotel_id,
            estado__in=[Reserva.CONFIRMADA, Reserva.REALIZADA],
            fecha_reserva__gte=fecha_inicio
        ).select_related('habitacion')

        if not reservas.exists():
            return pd.DataFrame()

        datos = []
        for r in reservas:
            duracion = (r.fecha_salida - r.fecha_entrada).days
            if duracion <= 0:
                continue

            precio_noche = float(r.total) / duracion
            if precio_noche <= 0 or precio_noche > 2000:
                continue  # OUTLIERS

            fecha = r.fecha_entrada

            datos.append({
                "mes": fecha.month,
                "temporada": self._calcular_temporada(fecha.month),
                "dia_semana": fecha.weekday(),
                "dias_anticipacion": (r.fecha_entrada - r.fecha_reserva).days,
                "duracion_estancia": duracion,
                "evento": self._detectar_evento_especial(fecha),
                "ocupacion": self._ocupacion_historica(hotel_id, fecha),
                "precio": precio_noche,
            })

        return pd.DataFrame(datos)

    # ---------------------------------------------------------------
    # Funciones auxiliares
    # ---------------------------------------------------------------
    def _calcular_temporada(self, mes):
        temp_alta = [12, 1, 7, 8]
        temp_media = [3, 4, 5, 6, 9]
        if mes in temp_alta: return 2
        if mes in temp_media: return 1
        return 0

    def _detectar_evento_especial(self, fecha):
        m, d = fecha.month, fecha.day
        if (m == 12 and d >= 20) or (m == 1 and d <= 7): return 1
        if m == 2 and 10 <= d <= 15: return 1
        if m in [3, 4] and 20 <= d <= 28: return 1
        if m == 8 and d in [6, 7]: return 1
        return 0

    def _ocupacion_historica(self, hotel_id, fecha):
        total = Habitacion.objects.filter(hotel_id=hotel_id).count()
        if total == 0:
            return 0

        ocupadas = Reserva.objects.filter(
            hotel_id=hotel_id,
            estado__in=[Reserva.CONFIRMADA, Reserva.REALIZADA],
            fecha_entrada__lte=fecha,
            fecha_salida__gte=fecha
        ).count()

        return round((ocupadas / total) * 100, 2)

    # ---------------------------------------------------------------
    # 2) Entrenar y guardar el modelo
    # ---------------------------------------------------------------
    def entrenar_modelo(self, hotel_id, tipo_habitacion):
        df = self.obtener_datos_historicos(hotel_id, tipo_habitacion)

        if df.empty or len(df) < self.min_datos_ml:
            return False, f"Datos insuficientes ({len(df)} registros)", 0

        X = df.drop(columns=["precio"])
        y = df["precio"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.modelo = RandomForestRegressor(
            n_estimators=260,
            max_depth=10,
            random_state=42
        )

        self.modelo.fit(X_train, y_train)
        self.r2_score = self.modelo.score(X_test, y_test)
        confianza = max(0, min(100, self.r2_score * 100))

        # Guardar modelo
        filename = f"{self.path_modelos}/hotel{hotel_id}_{tipo_habitacion}.pkl"
        dump(self.modelo, filename)

        return True, f"Modelo entrenado con {len(df)} registros", confianza

    # ---------------------------------------------------------------
    # 3) Predicción final
    # ---------------------------------------------------------------
    def predecir_precio(self, hotel_id, tipo_habitacion, fecha_objetivo=None):

        if fecha_objetivo is None:
            fecha_objetivo = datetime.now()

        # Intentar cargar el modelo
        filename = f"{self.path_modelos}/hotel{hotel_id}_{tipo_habitacion}.pkl"
        if os.path.exists(filename):
            self.modelo = load(filename)
        else:
            exito, msg, conf = self.entrenar_modelo(hotel_id, tipo_habitacion)
            if not exito:
                return self._precio_heuristico(hotel_id, tipo_habitacion, fecha_objetivo)

        # Features para predicción
        X_pred = np.array([[
            fecha_objetivo.month,
            self._calcular_temporada(fecha_objetivo.month),
            fecha_objetivo.weekday(),
            30,  # anticipación promedio
            2,   # estadía promedio
            self._detectar_evento_especial(fecha_objetivo),
            self._ocupacion_historica(hotel_id, fecha_objetivo),
        ]])

        precio_pred = self.modelo.predict(X_pred)[0]
        precio_pred = max(50, precio_pred)

        motivo = self._generar_motivo(fecha_objetivo)
        confianza = round(self.r2_score * 100, 2)

        return Decimal(str(round(precio_pred, 2))), confianza, motivo

    # ---------------------------------------------------------------
    # 4) Heurística de respaldo
    # ---------------------------------------------------------------
    def _precio_heuristico(self, hotel_id, tipo_habitacion, fecha):
        habitacion = Habitacion.objects.filter(
            tipo=tipo_habitacion,
            hotel_id=hotel_id
        ).first()

        if not habitacion:
            return Decimal("100.00"), 50.0, "Precio por defecto"

        precio_base = float(habitacion.precio_noche)

        temporada = self._calcular_temporada(fecha.month)
        evento = self._detectar_evento_especial(fecha)

        ajuste = 1.0
        motivo = ""

        if temporada == 2: ajuste, motivo = 1.25, "Temporada alta"
        elif temporada == 0: ajuste, motivo = 0.85, "Temporada baja"

        if evento:
            ajuste *= 1.15
            motivo += " + Evento especial"

        return Decimal(str(round(precio_base * ajuste, 2))), 70, motivo

    # ---------------------------------------------------------------
    # 5) Motivo explicativo
    # ---------------------------------------------------------------
    def _generar_motivo(self, fecha):
        motivos = []
        temp = self._calcular_temporada(fecha.month)

        if temp == 2: motivos.append("Temporada alta")
        elif temp == 0: motivos.append("Temporada baja")

        if self._detectar_evento_especial(fecha):
            motivos.append("Evento especial detectado")

        if not motivos:
            motivos.append("Basado en datos históricos + Random Forest")

        return " | ".join(motivos)

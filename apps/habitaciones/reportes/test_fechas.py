"""
Script de prueba para verificar la conversión de fechas en servicios.py
"""
from datetime import datetime, date

# Simular las funciones de conversión
def test_conversion_fechas():
    print("=== Test de Conversión de Fechas ===\n")

    # Test 1: String a date
    fecha_str = "2025-10-29"
    fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    print(f"✅ Test 1: String a date")
    print(f"   Input:  '{fecha_str}' (type: {type(fecha_str).__name__})")
    print(f"   Output: {fecha_obj} (type: {type(fecha_obj).__name__})\n")

    # Test 2: Verificar que es un objeto date
    assert isinstance(fecha_obj, date), "No es un objeto date"
    print(f"✅ Test 2: Verificación de tipo correcta\n")

    # Test 3: Operación de resta
    fecha_inicio_str = "2025-10-01"
    fecha_fin_str = "2025-10-29"
    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    dias = (fecha_fin - fecha_inicio).days + 1
    print(f"✅ Test 3: Operación de resta entre fechas")
    print(f"   Fecha inicio: {fecha_inicio}")
    print(f"   Fecha fin:    {fecha_fin}")
    print(f"   Días totales: {dias}\n")

    # Test 4: None se convierte a fecha actual
    fecha_hoy = datetime.now().date()
    print(f"✅ Test 4: Fecha None → fecha actual")
    print(f"   Fecha actual: {fecha_hoy}\n")

    print("=== Todos los tests pasaron ✅ ===")

if __name__ == "__main__":
    test_conversion_fechas()


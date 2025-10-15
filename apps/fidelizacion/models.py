from django.db import models
from apps.usuarios.models import User  # asegúrate de importar correctamente

class ProgramaFidelizacion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    descuento_maximo = models.IntegerField(
        help_text="Porcentaje máximo de descuento permitido (ej: 50 para 50%)"
    )
    activo = models.BooleanField(default=True)
    puntos_por_dolar_descuento = models.IntegerField(
        help_text="Puntos necesarios para obtener $1 de descuento (ej: 10 puntos = $1)"
    )
    def __str__(self):
        return self.nombre

class CuentaFidelizacion(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    fidelizacion = models.ForeignKey(ProgramaFidelizacion, on_delete=models.CASCADE)
    puntos_acumulados = models.IntegerField(default=0)
    
    def acumular_puntos(self, monto_gastado):
        """Gana puntos por compra: $1 gastado = 1 punto"""
        puntos_ganados = int(monto_gastado) 
        self.puntos_acumulados += puntos_ganados
        self.save()
        return puntos_ganados
    
    def calcular_descuento_disponible(self, total_cuenta):
        """Calcula el máximo descuento que puede aplicar"""
        # Valor máximo que puede descontar según el porcentaje límite
        descuento_maximo_permitido = (total_cuenta * self.fidelizacion.descuento_maximo) / 100
        
        # Valor que puede descontar según sus puntos (ej: 100 puntos / 10 = $10 de descuento)
        descuento_por_puntos = self.puntos_acumulados / self.fidelizacion.puntos_por_dolar_descuento
        
        return min(descuento_maximo_permitido, descuento_por_puntos)
    
    def canjear_puntos(self, monto_descuento):
        
        """Canjea puntos por descuento"""
        puntos_necesarios = int(monto_descuento * self.fidelizacion.puntos_por_dolar_descuento)
        if self.puntos_acumulados >= puntos_necesarios:
            self.puntos_acumulados -= puntos_necesarios
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.cliente.username} -Puntos {self.puntos_acumulados}"
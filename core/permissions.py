from rest_framework.permissions import BasePermission, SAFE_METHODS

class EscrituraPermitida(BasePermission):
    """
    Permiso que valida si la suscripción permite operaciones de escritura.
    Solo afecta a métodos no seguros (POST, PUT, PATCH, DELETE).
    """
    message = "Suscripción inactiva o vencida."
    
    def has_permission(self, request, view):
        # Permitir operaciones de lectura siempre
        if request.method in SAFE_METHODS:
            return True
        
        # Para operaciones de escritura, validar suscripción
        suscripcion = getattr(request, "suscripcion", None)
        return bool(suscripcion and suscripcion.puede_escribir)


class DentroDeCuota(BasePermission):
    """
    Permiso que valida si el tenant no ha excedido su cuota de recursos
    según su plan de suscripción.
    """
    message = "Cuota de plan alcanzada."
    
    def has_permission(self, request, view):
        # Obtener la suscripción del request
        suscripcion = getattr(request, "suscripcion", None)
        
        # Validar que existe suscripción activa
        if not suscripcion or not suscripcion.puede_escribir:
            self.message = "Suscripción inactiva o vencida."
            return False
        
        # Verificar si la vista está creando hoteles o usuarios
        creando_hoteles = getattr(view, "creando_hoteles", False)
        creando_usuarios = getattr(view, "creando_usuarios", False)
        
        # Obtener contadores actuales
        contadores = getattr(request, "contadores_tenant", {})
        
        # Validar límite de hoteles
        if creando_hoteles and contadores.get("hoteles", 0) >= suscripcion.plan.max_hoteles:
            self.message = f"Límite de hoteles alcanzado ({suscripcion.plan.max_hoteles})."
            return False
        
        # Validar límite de usuarios
        if creando_usuarios and contadores.get("usuarios", 0) >= suscripcion.plan.max_usuarios:
            self.message = f"Límite de usuarios alcanzado ({suscripcion.plan.max_usuarios})."
            return False
        
        return True

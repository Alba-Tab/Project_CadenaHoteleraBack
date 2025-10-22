from auditlog.registry import auditlog
from apps.reservas.models import Reserva
from apps.pagos.models import Pago
from apps.folioestancias.models import FolioEstancia
from apps.servicios.models import Servicio
from apps.habitaciones.models import Habitacion
from apps.checkinout.models import CheckInOut
from apps.usuarios.models import User
from apps.hoteles.models import Hotel

def register_audit_models():
    
    auditlog.register(Reserva)
    auditlog.register(Pago)
    auditlog.register(FolioEstancia)
    auditlog.register(Servicio)
    auditlog.register(Habitacion)
    auditlog.register(CheckInOut)
    auditlog.register(User)
    auditlog.register(Hotel)
  

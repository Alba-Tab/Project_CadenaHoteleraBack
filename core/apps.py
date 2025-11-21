from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """Ejecutar código cuando Django inicie"""
        print("🚀 CORE APP READY - INICIANDO FIREBASE...")
        logger.info("🚀 CORE APP READY - INICIANDO FIREBASE...")

        # Importar aquí para evitar circular imports
        from core.notifications_service import NotificationService

        # Inicializar Firebase en el arranque
        success = NotificationService._initialize_firebase()

        if success:
            print("✅ FIREBASE INICIALIZADO CORRECTAMENTE EN EL ARRANQUE")
            logger.info("✅ FIREBASE INICIALIZADO CORRECTAMENTE EN EL ARRANQUE")
        else:
            print("❌ ERROR: FIREBASE NO SE PUDO INICIALIZAR EN EL ARRANQUE")
            logger.error("❌ ERROR: FIREBASE NO SE PUDO INICIALIZAR EN EL ARRANQUE")

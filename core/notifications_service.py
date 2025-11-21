import firebase_admin
from firebase_admin import credentials, messaging
import logging
import os
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class NotificationService:
    """Servicio para enviar notificaciones push usando Firebase Cloud Messaging"""

    _initialized = False

    @classmethod
    def _initialize_firebase(cls):
        """Inicializar Firebase Admin SDK - solo una vez"""
        print("🔥 _initialize_firebase LLAMADO")
        logger.info("🔥 _initialize_firebase LLAMADO")
        
        if not cls._initialized and not firebase_admin._apps:
            try:
                print("🔥 Intentando inicializar Firebase...")
                logger.info("🔥 Intentando inicializar Firebase...")
                
                # Opción 1: Variable de entorno con JSON (producción AWS)
                if settings.FIREBASE_CREDENTIALS_JSON:
                    import json
                    print("🔥 Usando variable de entorno FIREBASE_CREDENTIALS_JSON")
                    logger.info("🔥 Usando variable de entorno FIREBASE_CREDENTIALS_JSON")
                    
                    cred_dict = json.loads(settings.FIREBASE_CREDENTIALS_JSON)
                    print(f"🔥 JSON parseado correctamente. Project ID: {cred_dict.get('project_id', 'N/A')}")
                    logger.info(f"🔥 JSON parseado correctamente. Project ID: {cred_dict.get('project_id', 'N/A')}")
                    
                    cred = credentials.Certificate(cred_dict)
                    print("✅ Firebase credential creado desde variable de entorno")
                    logger.info("✅ Firebase credential creado desde variable de entorno")
                # Opción 2: Archivo local (desarrollo)
                else:
                    print("🔥 Usando archivo local de credenciales")
                    logger.info("🔥 Usando archivo local de credenciales")
                    
                    cred_path = settings.FIREBASE_CREDENTIAL_PATH
                    if not os.path.exists(cred_path):
                        print(f"❌ Archivo no encontrado: {cred_path}")
                        logger.error(f"❌ Archivo no encontrado: {cred_path}")
                        return False
                    cred = credentials.Certificate(cred_path)
                    print("✅ Firebase credential creado desde archivo local")
                    logger.info("✅ Firebase credential creado desde archivo local")

                # Inicializar Firebase
                print("🔥 Llamando a firebase_admin.initialize_app()...")
                logger.info("🔥 Llamando a firebase_admin.initialize_app()...")
                
                firebase_admin.initialize_app(cred)

                cls._initialized = True
                print("✅✅✅ FIREBASE ADMIN SDK INICIALIZADO CORRECTAMENTE ✅✅✅")
                logger.info("✅✅✅ FIREBASE ADMIN SDK INICIALIZADO CORRECTAMENTE ✅✅✅")
                return True

            except Exception as e:
                print(f"❌❌❌ ERROR INICIALIZANDO FIREBASE: {str(e)} ❌❌❌")
                logger.error(f"❌❌❌ ERROR INICIALIZANDO FIREBASE: {str(e)} ❌❌❌")
                import traceback
                print(f"❌ Traceback: {traceback.format_exc()}")
                logger.error(f"❌ Traceback: {traceback.format_exc()}")
                return False

        print("🔥 Firebase ya estaba inicializado")
        logger.info("🔥 Firebase ya estaba inicializado")
        return True

    @classmethod
    def send_to_token(cls, token, title, body, data=None):
        """
        Enviar notificación a un token específico

        Args:
            token (str): Token FCM del dispositivo
            title (str): Título de la notificación
            body (str): Mensaje de la notificación
            data (dict): Datos adicionales (opcional)

        Returns:
            bool: True si se envió correctamente, False si falló
        """
        if not cls._initialize_firebase():
            return False

        try:
            # Convertir todos los valores de data a string (Firebase lo requiere)
            string_data = {}
            if data:
                string_data = {k: str(v) for k, v in data.items()}

            # Crear el mensaje
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=string_data,
                token=token
            )

            # Enviar mensaje
            response = messaging.send(message)
            logger.info(f"Notificación enviada exitosamente. ID: {response}")
            return True

        except messaging.UnregisteredError:
            logger.warning(f"Token FCM inválido o expirado: {token}")
            return False
        except Exception as e:
            logger.error(f"Error enviando notificación: {str(e)}")
            return False

    @classmethod
    def send_to_user(cls, usuario, title, body, data=None):
        """
        Enviar notificación a un usuario específico

        Args:
            usuario: Instancia del modelo Usuario
            title (str): Título de la notificación
            body (str): Mensaje de la notificación
            data (dict): Datos adicionales (opcional)

        Returns:
            bool: True si se envió correctamente, False si falló
        """
        if not hasattr(usuario, 'fcm_token') or not usuario.fcm_token:
            logger.warning(f"Usuario {usuario.username} no tiene token FCM")
            return False

        logger.info(f"✅ Usuario {usuario.username} tiene token FCM: {usuario.fcm_token[:20]}...")

        return cls.send_to_token(
            token=usuario.fcm_token,
            title=title,
            body=body,
            data=data
        )

    @classmethod
    def send_to_group(cls, group_name, title, body, data=None):
        """
        Enviar notificación a todos los usuarios de un grupo/rol específico

        Args:
            group_name (str): Nombre del grupo (ej: 'Huéspedes', 'Administradores')
            title (str): Título de la notificación
            body (str): Mensaje de la notificación
            data (dict): Datos adicionales (opcional)

        Returns:
            int: Número de notificaciones enviadas exitosamente
        """
        if not cls._initialize_firebase():
            return 0

        from apps.usuarios.models import User

        # Obtener usuarios del grupo específico con token FCM
        usuarios = User.objects.filter(
            groups__name=group_name,
            is_active=True,
            fcm_token__isnull=False
        ).exclude(fcm_token='')

        success_count = 0
        for usuario in usuarios:
            if cls.send_to_user(usuario, title, body, data):
                success_count += 1

        logger.info(f"Notificaciones enviadas a {success_count}/{usuarios.count()} usuarios del grupo '{group_name}'")
        return success_count

    @classmethod
    def send_to_multiple_tokens(cls, tokens, title, body, data=None):
        """
        Enviar notificación a múltiples tokens usando multicast

        Args:
            tokens (list): Lista de tokens FCM
            title (str): Título de la notificación
            body (str): Mensaje de la notificación
            data (dict): Datos adicionales (opcional)

        Returns:
            dict: Diccionario con información del envío
        """
        if not cls._initialize_firebase():
            return {'success_count': 0, 'failure_count': len(tokens)}

        if not tokens:
            logger.warning("Lista de tokens vacía")
            return {'success_count': 0, 'failure_count': 0}

        try:
            # Crear mensaje multicast
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens
            )

            # Enviar a todos los tokens - FUNCIÓN CORRECTA para v7.x
            response = messaging.send_each_for_multicast(message)

            logger.info(f"Notificaciones enviadas: {response.success_count}/{len(tokens)}")

            # Manejar tokens inválidos
            failed_tokens = []
            if response.failure_count > 0:
                for idx, resp in enumerate(response.responses):
                    if not resp.success:
                        failed_tokens.append(tokens[idx])
                        logger.warning(f"Token fallido: {tokens[idx]} - Error: {resp.exception}")

                # Limpiar tokens inválidos
                cls._cleanup_invalid_tokens(failed_tokens)

            return {
                'success_count': response.success_count,
                'failure_count': response.failure_count,
                'failed_tokens': failed_tokens
            }

        except Exception as e:
            logger.error(f"Error enviando notificaciones múltiples: {str(e)}")
            return {'success_count': 0, 'failure_count': len(tokens)}

    @classmethod
    def _cleanup_invalid_tokens(cls, invalid_tokens):
        """
        Limpiar tokens FCM inválidos de la base de datos

        Args:
            invalid_tokens (list): Lista de tokens inválidos
        """
        if not invalid_tokens:
            return

        try:
            from apps.usuarios.models import User

            updated_count = User.objects.filter(
                fcm_token__in=invalid_tokens
            ).update(fcm_token=None)

            logger.info(f"Limpiados {updated_count} tokens FCM inválidos de la base de datos")

        except Exception as e:
            logger.error(f"Error limpiando tokens inválidos: {str(e)}")

    @classmethod
    def send_reserva_notification(cls, usuario, reserva_id, mensaje="", notification_type="confirmacion"):
        """
        Método específico para notificaciones de reservas

        Args:
            usuario: Usuario huésped
            reserva_id: ID de la reserva
            mensaje (str): Mensaje personalizado
            notification_type (str): Tipo de notificación (confirmacion, recordatorio, checkin, checkout)

        Returns:
            bool: True si se envió correctamente
        """
        titles = {
            'confirmacion': 'Reserva Confirmada',
            'recordatorio': 'Recordatorio de Reserva',
            'checkin': 'Check-in Disponible',
            'checkout': 'Check-out Pendiente'
        }

        title = titles.get(notification_type, 'Notificación de Reserva')
        body = mensaje if mensaje else f"Tu reserva #{reserva_id} ha sido procesada"

        data = {
            'type': 'reserva',
            'notification_type': notification_type,
            'reserva_id': str(reserva_id),
            'timestamp': str(timezone.now())
        }

        return cls.send_to_user(usuario, title, body, data)

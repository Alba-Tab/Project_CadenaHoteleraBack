from django.utils.deprecation import MiddlewareMixin
from auditlog.context import set_actor, disable_auditlog
from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTActorMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # Intenta autenticar el usuario desde el token JWT
        try:
            jwt_auth = JWTAuthentication()
            user_auth_tuple = jwt_auth.authenticate(request)
            if user_auth_tuple is not None:
                user, token = user_auth_tuple
                request.user = user
                set_actor(user)  # <- le dice a auditlog quién es el actor
        except Exception:
            disable_auditlog()  # Evita registrar acciones anónimas
        return None

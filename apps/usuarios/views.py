from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from django.db import transaction
from django_tenants.utils import schema_context
from .models import User
from .serializers import UserSerializer, RoleSerializer, PermissionSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from apps.suscripciones.models import UsoTenant

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar todos los permisos disponibles
    Solo lectura - no se pueden crear/editar permisos desde aquí
    """
    permission_classes = [IsAuthenticated]  # ✨ CAMBIADO
    # queryset = Permission.objects.all().order_by('name')
    serializer_class = PermissionSerializer

    def get_queryset(self):
        """
        Filtrar solo permisos de las apps del hotel y gestión de usuarios
        """
        # Apps relevantes para tu sistema hotelero
        relevant_apps = [
            'usuarios',      # Gestión de usuarios
            'hoteles',       # Hoteles
            'habitaciones',  # Habitaciones
            'reservas',      # Reservas
            'servicios',     # Servicios
            'pagos',         # Pagos
            'fidelizacion',  # Fidelización
            'checkinout',    # Check-in/out
            'folioestancias', # Folios
            'auth',          # Roles y permisos (Group/Permission)
        ]

        return Permission.objects.filter(
            content_type__app_label__in=relevant_apps
        ).order_by('content_type__app_label', 'name')

class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar roles (crear, editar, eliminar)
    Ahora incluye asignación de permisos directamente en crear/editar
    """
    permission_classes = [IsAuthenticated]  # ✨ CAMBIADO
    queryset = Group.objects.all().order_by('name')
    serializer_class = RoleSerializer

    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """
        Endpoint para ver solo los permisos de un rol específico
        GET /api/roles/{id}/permissions/
        """
        role = self.get_object()
        permissions = role.permissions.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios + autenticación JWT
    """
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_permissions(self):
        """
        Permisos diferentes según la acción
        """
        if self.action in ['login', 'register', 'refresh_token']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @transaction.atomic
    def perform_create(self, serializer):
        """
        Crea un usuario y actualiza el contador del tenant
        """
        # Guardar el usuario
        serializer.save()
        
        # Actualizar contador si hay tenant
        if hasattr(self.request, 'tenant') and self.request.tenant:
            total_usuarios = User.objects.count()
            
            with schema_context("public"):
                uso, _ = UsoTenant.objects.select_for_update().get_or_create(tenant=self.request.tenant)
                uso.usuarios = total_usuarios
                uso.ultima_actualizacion = timezone.now()
                uso.save()
    
    @transaction.atomic
    def perform_destroy(self, instance):
        """
        Elimina un usuario y actualiza el contador del tenant
        """
        # Guardar referencia al tenant antes de eliminar
        tenant = self.request.tenant if hasattr(self.request, 'tenant') else None
        
        # Eliminar el usuario
        instance.delete()
        
        # Actualizar contador si hay tenant
        if tenant:
            total_usuarios = User.objects.count()
            
            with schema_context("public"):
                uso = UsoTenant.objects.select_for_update().get(tenant=tenant)
                uso.usuarios = total_usuarios
                uso.ultima_actualizacion = timezone.now()
                uso.save()

    # ✨ MÉTODOS DE AUTENTICACIÓN JWT

    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Login de usuario con JWT
        POST /api/usuarios/login/
        Body: {"username": "...", "password": "..."}
        """
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'error': 'Username y password son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user:
            if not user.is_active:
                return Response({
                    'error': 'Usuario desactivado'
                }, status=status.HTTP_403_FORBIDDEN)

            # ✨ Crear tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Actualizar último login
            user.last_login = timezone.now()
            user.save()

            # Obtener permisos del usuario
            permissions = []
            for group in user.groups.all():
                for permission in group.permissions.all():
                    permissions.append(permission.codename)

            # Obtener roles
            roles = [group.name for group in user.groups.all()]

            serializer = UserSerializer(user)
            return Response({
                'access_token': str(access_token),
                'refresh_token': str(refresh),
                'user': serializer.data,
                'permissions': permissions,
                'roles': roles,
                'hotel_id': user.hotel.id if user.hotel else None,
                'message': '¡Login exitoso!'
            })

        return Response({
            'error': 'Credenciales incorrectas'
        }, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def register(self, request):
        """
        Registro de nuevo usuario con JWT
        POST /api/usuarios/register/
        Body (multipart/form-data):
            - username: str (requerido)
            - password: str (requerido)
            - email: str (requerido)
            - first_name: str (opcional)
            - last_name: str (opcional)
            - photo: file (opcional - imagen)
        """
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        photo = request.FILES.get('photo')

        # Validaciones básicas
        if not username or not password:
            return Response({
                'error': 'Username y password son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 8:
            return Response({
                'error': 'La contraseña debe tener al menos 8 caracteres'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si el username ya existe
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'El username ya está en uso'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si el email ya existe (si se proporciona)
        if email and User.objects.filter(email=email).exists():
            return Response({
                'error': 'El email ya está en uso'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validar tipo de archivo si se envía foto
        if photo:
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            file_extension = photo.name.lower()[photo.name.rfind('.'):]
            if file_extension not in allowed_extensions:
                return Response({
                    'error': 'Solo se permiten imágenes (jpg, jpeg, png, gif, webp)'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Crear usuario
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        # Asignar foto si se proporcionó
        if photo:
            user.photo = photo
            user.save()

        # Asignar rol por defecto (por ejemplo, "Huesped")
        try:
            huesped_role = Group.objects.get(name='Huesped')
            user.groups.add(huesped_role)
        except Group.DoesNotExist:
            pass

        # Actualizar contador de usuarios del tenant
        if hasattr(request, 'tenant') and request.tenant:
            total_usuarios = User.objects.count()
            
            with schema_context("public"):
                uso, _ = UsoTenant.objects.select_for_update().get_or_create(tenant=request.tenant)
                uso.usuarios = total_usuarios
                uso.ultima_actualizacion = timezone.now()
                uso.save()

        # Generar tokens JWT automáticamente
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        serializer = UserSerializer(user)
        return Response({
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'user': serializer.data,
            'message': '¡Registro exitoso!'
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Logout de usuario con JWT
        POST /api/usuarios/logout/
        Body: {"refresh_token": "..."}
        """
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # Invalidar token
            return Response({
                'message': 'Logout exitoso'
            })
        except TokenError:
            return Response({
                'error': 'Token inválido'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def refresh_token(self, request):
        """
        Renovar access token usando refresh token
        POST /api/usuarios/refresh_token/
        Body: {"refresh_token": "..."}
        """
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({
                    'error': 'refresh_token requerido'
                }, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token

            return Response({
                'access_token': str(access_token)
            })
        except TokenError:
            return Response({
                'error': 'Refresh token inválido o expirado'
            }, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Obtener información del usuario actual
        GET /api/usuarios/me/
        """
        user = request.user
        serializer = UserSerializer(user)

        # Obtener permisos
        permissions = []
        for group in user.groups.all():
            for permission in group.permissions.all():
                permissions.append(permission.codename)

        # Obtener roles
        roles = [group.name for group in user.groups.all()]

        return Response({
            'user': serializer.data,
            'permissions': permissions,
            'roles': roles,
            'hotel_id': user.hotel.id if user.hotel else None,
            'photo_url': user.photo.url if user.photo else None,
            'is_admin': user.is_superuser,
            'last_login': user.last_login,
            'total_permissions': len(permissions)
        })

    @action(detail=False, methods=['put', 'patch'])
    def updateprofile(self, request):
        """
        Actualizar perfil del usuario actual
        PUT/PATCH /api/usuarios/updateprofile/
        Body (multipart/form-data o JSON):
            - first_name: str (opcional)
            - last_name: str (opcional)
            - email: str (opcional)
            - photo: file (opcional - imagen)
        """
        user = request.user
        
        # Obtener datos
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        photo = request.FILES.get('photo')

        # Validar email único (si se proporciona y es diferente al actual)
        if email and email != user.email:
            if User.objects.filter(email=email).exists():
                return Response({
                    'error': 'El email ya está en uso'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.email = email

        # Actualizar campos de texto
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name

        # Validar y actualizar foto si se envía
        if photo:
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            file_extension = photo.name.lower()[photo.name.rfind('.'):]
            if file_extension not in allowed_extensions:
                return Response({
                    'error': 'Solo se permiten imágenes (jpg, jpeg, png, gif, webp)'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.photo = photo

        # Guardar cambios
        user.save()

        # Serializar y devolver
        serializer = UserSerializer(user)
        return Response({
            'user': serializer.data,
            'photo_url': user.photo.url if user.photo else None,
            'message': 'Perfil actualizado exitosamente'
        })

    @action(detail=False, methods=['get'])
    def misreservas(self, request):
        """
        Obtener el historial de reservas del usuario actual
        GET /api/usuarios/misreservas/
        """
        from apps.reservas.models import Reserva
        from apps.reservas.serializers import ReservaSerializer

        user = request.user

        # Obtener todas las reservas del usuario, ordenadas por más reciente
        reservas = Reserva.objects.filter(huesped=user).order_by('-fecha_reserva')

        serializer = ReservaSerializer(reservas, many=True)

        return Response({
            'usuario': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'nombre_completo': f"{user.first_name} {user.last_name}".strip() or user.username
            },
            'reservas': serializer.data,
            'total_reservas': reservas.count()
        })



    @action(detail=False, methods=['put'])
    def change_password(self, request):
        """
        Cambiar contraseña del usuario actual
        PUT /api/usuarios/change_password/
        Body: {"old_password": "...", "new_password": "..."}
        """
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({
                'error': 'old_password y new_password son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.check_password(old_password):
            return Response({
                'error': 'Contraseña actual incorrecta'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            return Response({
                'error': 'La nueva contraseña debe tener al menos 8 caracteres'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Cambiar contraseña
        request.user.set_password(new_password)
        request.user.save()

        # Generar nuevos tokens JWT
        refresh = RefreshToken.for_user(request.user)
        access_token = refresh.access_token

        return Response({
            'message': 'Contraseña cambiada exitosamente',
            'access_token': str(access_token),
            'refresh_token': str(refresh)
        })

    @action(detail=False, methods=['get'])
    def verify_token(self, request):
        """
        Verificar si el token JWT es válido
        GET /api/usuarios/verify_token/
        """
        return Response({
            'valid': True,
            'user_id': request.user.id,
            'username': request.user.username,
            'email': request.user.email
        })

    @action(detail=False, methods=['post'])
    def actualizar_token_fcm(self, request):
        """
        Actualizar token FCM para notificaciones push
        POST /api/usuarios/actualizar_token_fcm/
        Body: {"fcm_token": "..."}
        """
        usuario = request.user
        fcm_token = request.data.get('fcm_token')

        if not fcm_token:
            return Response({
                'error': 'fcm_token es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)

        usuario.fcm_token = fcm_token
        usuario.save()

        return Response({
            'message': 'Token FCM actualizado exitosamente',
            'fcm_token': fcm_token
        })

    @action(detail=False, methods=['post'])
    def eliminar_token_fcm(self, request):
        """
        Eliminar token FCM (cuando cierra sesión o desinstala app)
        POST /api/usuarios/eliminar_token_fcm/
        """
        usuario = request.user
        usuario.fcm_token = None
        usuario.save()

        return Response({
            'message': 'Token FCM eliminado exitosamente'
        })

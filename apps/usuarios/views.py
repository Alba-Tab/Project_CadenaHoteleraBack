from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from .models import User
from .serializers import UserSerializer, RoleSerializer, PermissionSerializer

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar todos los permisos disponibles
    Solo lectura - no se pueden crear/editar permisos desde aquí
    """
    permission_classes = [IsAuthenticated]  # ✨ CAMBIADO
    queryset = Permission.objects.all().order_by('name')
    serializer_class = PermissionSerializer

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

    def get_permissions(self):
        """
        Permisos diferentes según la acción
        """
        if self.action in ['login', 'register', 'refresh_token']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

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
                'message': '¡Login exitoso!'
            })

        return Response({
            'error': 'Credenciales incorrectas'
        }, status=status.HTTP_401_UNAUTHORIZED)

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
            'is_admin': user.is_superuser,
            'last_login': user.last_login,
            'total_permissions': len(permissions)
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

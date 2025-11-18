from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from .models import User

class PermissionSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type','label']


    def get_label(self, obj):
        traducciones = {
            'add_': 'Agregar',
            'change_': 'Editar',
            'delete_': 'Eliminar',
            'view_': 'Ver',
        }
        for pref, verbo in traducciones.items():
            if obj.codename.startswith(pref):
                modelo = obj.content_type.model.replace('_', ' ').capitalize()
                return f"{verbo} {modelo}"
        # Si es un permiso personalizado, usamos su nombre tal cual
        return obj.name

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_count = serializers.SerializerMethodField()
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'permission_count', 'permission_ids']

    def get_permission_count(self, obj):
        return obj.permissions.count()

    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        role = Group.objects.create(**validated_data)
        if permission_ids:
            role.permissions.set(permission_ids)
        return role

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        instance = super().update(instance, validated_data)
        if permission_ids is not None:
            instance.permissions.set(permission_ids)
        return instance


class UserSerializer(serializers.ModelSerializer):
    groups = RoleSerializer(many=True, read_only=True)
    group_ids = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        write_only=True,
        source='groups',
        required=False
    )
    password = serializers.CharField(write_only=True)
    photo = serializers.ImageField(required=False, allow_null=True)
    photo_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups', 'group_ids', 'password', 
                  'first_name', 'last_name', 'photo', 'photo_url']

    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

    def create(self, validated_data):
        password = validated_data.pop('password')
        groups = validated_data.pop('groups', [])
        photo = validated_data.pop('photo', None)
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        if groups:
            user.groups.set(groups)
        if photo:
            user.photo = photo
        user.save()
        
        # Indexar rostro en Rekognition
        if photo:
            try:
                from apps.facial_recognition.services import FacialRecognitionService
                FacialRecognitionService.index_face(user.id, user.photo.name)
            except Exception as e:
                print(f"⚠️ Error indexando rostro: {e}")
        
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        groups = validated_data.pop('groups', None)
        photo = validated_data.pop('photo', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        if groups is not None:
            instance.groups.set(groups)
        
        # Manejar foto por separado
        if photo is not None:
            try:
                instance.photo = photo
                instance.save()
                
                # Re-indexar rostro
                try:
                    from apps.facial_recognition.services import FacialRecognitionService
                    FacialRecognitionService.index_face(instance.id, instance.photo.name)
                except Exception as e:
                    print(f"⚠️ Error re-indexando rostro: {e}")
            except Exception as e:
                print(f"⚠️ Error guardando foto en S3: {e}")
                # Guardar sin foto si falla S3
                update_fields = [f.name for f in instance._meta.fields if f.name != 'photo' and f.name != 'id']
                instance.save(update_fields=update_fields)
                raise serializers.ValidationError(f"Error al subir la foto: {str(e)}")
        else:
            # Guardar sin tocar el campo photo
            # Obtener todos los campos del modelo excepto photo
            update_fields = [f.name for f in instance._meta.fields if f.name != 'photo' and f.name != 'id']
            instance.save(update_fields=update_fields)
        
        return instance

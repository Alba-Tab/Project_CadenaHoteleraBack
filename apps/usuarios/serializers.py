from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from .models import User

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']



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

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups', 'group_ids', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

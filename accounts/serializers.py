from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

def check_admin_promotion(serializer, attrs):
    # Granting administrador requires the requester to re-enter their own password
    admin_password = attrs.pop('admin_password', None)
    current = getattr(serializer.instance, 'type', None)
    if attrs.get('type') == User.UserType.ADMIN and current != User.UserType.ADMIN:
        user = serializer.context['request'].user
        if not admin_password or not user.check_password(admin_password):
            raise PermissionDenied('admin_password is required and must match your password to grant administrador.')
    return attrs

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    re_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    admin_password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'password', 're_password', 'name', 'first_lastname', 'type', 'admin_password']

    def validate_password(self, password):
        try:
            validate_password(password)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return password

    def validate(self, data):
        if data['password'] != data['re_password']:
            raise serializers.ValidationError({'re_password': 'Passwords do not match.'})
        return check_admin_promotion(self, data)

    def create(self, validated_data):
        validated_data.pop('re_password')
        return User.objects.create_user(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    admin_password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = (
            'id', 'email', 'name', 'first_lastname', 'second_lastname',
            'type', 'phone', 'position', 'is_active', 'date_registered', 'admin_password',
        )
        read_only_fields = ('id', 'date_registered')

    def validate(self, attrs):
        return check_admin_promotion(self, attrs)

class SelfUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = (
        'id',
        'name', 
        'first_lastname',
        'type',
    )
    read_only_fields = ('name', 'first_lastname', 'type',)
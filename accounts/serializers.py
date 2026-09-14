from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    re_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['nickname', 'password', 're_password', 'name', 'first_lastname']

    def validate_password(self, password):
        try:
            validate_password(password)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return password

    def validate(self, data):
        if data['password'] != data['re_password']:
            raise serializers.ValidationError({'re_password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('re_password')
        return User.objects.create_user(**validated_data)

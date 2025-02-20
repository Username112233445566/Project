from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from django.contrib.auth.password_validation import get_default_password_validators


class UserAvatarNickanmeSerializer(serializers.Serializer):
    username = serializers.CharField()
    avatar = serializers.ImageField()


class UserEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)


class VerifySerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    otp = serializers.CharField(max_length=4, required=True)


class UserLoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()


class AdminLoginSerializer(serializers.Serializer):
    login = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'apartment_number', 'address', 'password', 'number')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apartment_number', 'password', 'address', 'number', 'avatar', 'is_confirmed', 'is_denied', 'created_at']

    def get_created_at(self, obj) -> str:
        return obj.created_at.strftime('%d.%m.%Y') if obj.created_at else None


class UserPutSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['is_confirmed', 'number', 'avatar', 'password', 'is_denied']
        extra_kwargs = {
            'is_confirmed': {'required': False},
            'number': {'required': False},
            'avatar': {'required': False},
            'password': {'required': False},
            'is_denied': {'required': False},
        }
    
    def validate_password(self, value):
        if value:
            self.validate_password_complexity(value)
        return value

    def validate_password_complexity(self, password):
        validators = get_default_password_validators()
        for validator in validators:
            validator.validate(password)

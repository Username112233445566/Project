from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from typing import Tuple
from django.contrib.auth import logout
from django.utils import timezone


class OTPService:
    @staticmethod
    def generate_verification_code() -> str:
        """Генерирует 4-значный OTP код."""
        return get_random_string(4, allowed_chars='123456789')

    @staticmethod
    def save_user_otp(user: User, otp: str):
        """Сохраняет OTP код в модели пользователя и фиксирует время его создания."""
        user.code = otp
        user.otp_created_at = timezone.now()
        user.save()

    @staticmethod
    def is_otp_expired(user: User) -> bool:
        """Проверяет, истёк ли OTP код (15 минут)."""
        if user.otp_created_at:
            expiration_time = user.otp_created_at + timezone.timedelta(minutes=15)
            if timezone.now() > expiration_time:
                return True
        return False

    @staticmethod
    def verify_user_otp(user: User, otp: str) -> bool:
        """Проверяет правильность OTP кода и истечение срока действия."""
        if OTPService.is_otp_expired(user):
            user.code = None
            user.save()
            return False
        return user.code == otp

    @staticmethod
    def forgot_password(validated_data):
        """Генерирует и отправляет OTP код на email пользователя для сброса пароля."""
        email = validated_data['email']
        verification_code = OTPService.generate_verification_code()

        user = User.objects.filter(email=email).first()

        if user:
            OTPService.save_user_otp(user, verification_code)
            send_mail(
                'OTP код для сброса пароля',
                f'Ваш новый OTP код: {verification_code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            return {'user_id': user.id, 'detail': 'OTP код отправлен на ваш email.'}, status.HTTP_200_OK
        else:
            return {'detail': 'Пользователь не найден.'}, status.HTTP_404_NOT_FOUND


class AuthService:
    @staticmethod
    def generate_tokens(user: User) -> dict:
        """Генерирует JWT токены для пользователя."""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def confirmed_user(user: User):
        """Пользовател в ожидании подтверждения."""
        user.is_confirmed = False
        user.code = None
        user.save()

    @staticmethod
    def register_user(validated_data) -> dict:
        """Логика для регистрации пользователя."""
        email = validated_data['email']
        verification_code = OTPService.generate_verification_code()

        user, created = User.objects.get_or_create(email=email, defaults={
            'username': validated_data.get('username'),
            'address': validated_data.get('address'),
            'apartment_number': validated_data.get('apartment_number'),
            'password': validated_data.get('password'),
            'number': validated_data.get('number'),
        })

        OTPService.save_user_otp(user, verification_code)
        send_mail(
            'OTP код',
            f'Ваш новый OTP код: {verification_code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )
        message = {'detail': 'OTP код отправлен на ваш email.'}

        return {
            'user_id': user.id,
            'detail': message,
            'tokens': AuthService.generate_tokens(user) if created else {}
        }
    
    @staticmethod
    def resend_otp(email: str) -> dict:
        """Логика для повторной отправки OTP кода."""
        user = User.objects.filter(email=email).first()

        if not user:
            return {'detail': 'Пользователь с таким email не найден.'}

        verification_code = OTPService.generate_verification_code()
        OTPService.save_user_otp(user, verification_code)

        send_mail(
            'OTP код',
            f'Ваш OTP код: {verification_code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )

        return {'detail': 'OTP код повторно отправлен на ваш email.'}

    @staticmethod
    def verify_otp(validated_data) -> Tuple[dict, int]:
        """Логика для верификации OTP кода."""
        email = validated_data['email']
        otp = validated_data['otp']

        try:
            user = User.objects.get(email=email)

            if not OTPService.verify_user_otp(user, otp):
                return {'detail': 'Неверный OTP код.'}, status.HTTP_400_BAD_REQUEST

            if not user.is_confirmed:
                AuthService.confirmed_user(user)
                return {'detail': 'Пользователь в ожидания подтверждения.'}, status.HTTP_200_OK

        except User.DoesNotExist:
            return {'detail': 'Пользователь не найден.'}, status.HTTP_404_NOT_FOUND

    @staticmethod
    def login_user(validated_data) -> Tuple[dict, int]:
        """Логика для входа пользователя."""
        password = validated_data['password']
        email = validated_data['email']

        user = User.objects.filter(password=password, email=email).first()

        if user and user.is_confirmed == True:
            tokens = AuthService.generate_tokens(user)
            return {'user_id': user.id, 'detail': 'Успешный вход.', 'tokens': tokens}, status.HTTP_200_OK
        return {'detail': 'Неверный email или пароль.'}, status.HTTP_401_UNAUTHORIZED

    @staticmethod
    def logout_user(validated_data, request) -> Tuple[dict, int]:
        """Логика logout для пользователя."""
        email = validated_data['email']

        user = User.objects.filter(email=email).first()

        if user:
            logout(request)
            return {'user_id': user.id, 'detail': 'Успешный выход.'}, status.HTTP_200_OK
        return {'detail': 'Неверный email.'}, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def login_admin(validated_data) -> Tuple[dict, int]:    
        """Логика для входа администратора."""
        login = validated_data['login']
        password = validated_data['password']

        user = User.objects.filter(password=password, login=login).first()

        if user and user.is_staff:
            tokens = AuthService.generate_tokens(user)
            return {'user_id': user.id, 'detail': 'Успешный вход.', 'tokens': tokens}, status.HTTP_200_OK
        return {'detail': 'Неверный логин или пароль.'}, status.HTTP_401_UNAUTHORIZED
    
    @staticmethod
    def save_password(user, validated_data):
        """
        Обрабатывает и сохраняет данные пользователя, включая пароль.
        """
        if 'password' in validated_data:
            if user.is_superuser:
                user.set_password(validated_data['password'])
            else:
                user.password = validated_data['password']
            validated_data.pop('password')
        for attr, value in validated_data.items():
            setattr(user, attr, value)        
        user.save()
        return user


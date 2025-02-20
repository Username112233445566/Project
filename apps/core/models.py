from django.contrib.auth.models import AbstractUser
from django.db import models
from .manager import UserManager
from django.utils import timezone
from django.core.exceptions import ValidationError


class User(AbstractUser):
    username = models.CharField(max_length=20, null=True, blank=True, verbose_name="Имя пользователя")
    email = models.EmailField(max_length=50, unique=True, verbose_name="Email")
    number = models.CharField(max_length=16, null=True, blank=True, verbose_name="Номер телефона")
    avatar = models.ImageField(upload_to='avatar/', verbose_name="Фото профиля", null=True, blank=True)
    address = models.TextField(max_length=50, null=True, blank=True, verbose_name="Адрес")
    apartment_number = models.CharField(max_length=5, null=True, blank=True, verbose_name="Номер квартиры")
    order_number = models.CharField(max_length=4, null=True, blank=True, verbose_name="Номер заказа")
    login = models.CharField(max_length=20, null=True, blank=True, verbose_name="Логин")
    is_confirmed = models.BooleanField(default=False, verbose_name="Подтвержденный")
    is_staff = models.BooleanField(default=False, verbose_name='Статус персонала')
    code = models.CharField(max_length=4, null=True, blank=True, verbose_name="Код подтверждения")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    is_denied = models.BooleanField(default=False, verbose_name='Отказ')
    otp_created_at = models.DateTimeField(null=True, blank=True, verbose_name="Время создания OTP")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username or self.email or 'Пользователь'

    def clean(self):
        if self.is_confirmed and self.is_denied:
            raise ValidationError("Пользователь не может быть одноврменно подтвержденным и отклоненным")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

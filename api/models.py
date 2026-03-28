# api/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class User(AbstractUser):
    """Кастомная модель пользователя"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class ProxyToken(models.Model):
    """Модель токена доступа - без связей с User"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    traffic_limit_mb = models.IntegerField(default=1024)
    traffic_used_mb = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Токен доступа"
        verbose_name_plural = "Токены доступа"

    def __str__(self):
        return self.token[:20]

    @property
    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at < timezone.now():
            return False
        if self.traffic_limit_mb > 0 and self.traffic_used_mb >= self.traffic_limit_mb:
            return False
        return True

    @property
    def get_status_display(self):
        if not self.is_active:
            return "Неактивен"
        if self.expires_at < timezone.now():
            return "Истек"
        if self.traffic_limit_mb > 0 and self.traffic_used_mb >= self.traffic_limit_mb:
            return "Лимит исчерпан"
        return "Доступен"


class VPSServer(models.Model):
    """Модель прокси-сервера"""
    STATUS_CHOICES = [
        ('free', 'Свободен'),
        ('busy', 'Занят'),
        ('error', 'Ошибка'),
        ('maintenance', 'Обслуживание'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='free')
    busy_since = models.DateTimeField(null=True, blank=True)

    ip_address = models.GenericIPAddressField(default='192.168.56.105')
    proxy_port = models.IntegerField(default=3128)
    proxy_username = models.CharField(max_length=50, default='username')
    proxy_password = models.CharField(max_length=255, default='password')
    connection_method = models.CharField(max_length=100, default='HTTP-прокси с аутентификацией')

    last_checked = models.DateTimeField(null=True, blank=True)
    last_online = models.DateTimeField(null=True, blank=True)
    response_time_ms = models.IntegerField(default=0)

    total_connections = models.IntegerField(default=0)
    total_time_seconds = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Прокси-сервер"
        verbose_name_plural = "Прокси-серверы"

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def is_available(self):
        return self.status == 'free'

    def get_connection_url(self):
        return f"http://{self.proxy_username}:{self.proxy_password}@{self.ip_address}:{self.proxy_port}"

    def assign_to_token(self):
        if not self.is_available:
            return False
        self.status = 'busy'
        self.busy_since = timezone.now()
        self.total_connections += 1
        self.save()
        return True

    def release(self):
        if self.status == 'busy' and self.busy_since:
            self.total_time_seconds += (timezone.now() - self.busy_since).seconds
        self.status = 'free'
        self.busy_since = None
        self.save()


class ActiveConnection(models.Model):
    """Модель активного подключения"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.OneToOneField(ProxyToken, on_delete=models.CASCADE, related_name='connection')
    server = models.OneToOneField(VPSServer, on_delete=models.CASCADE, related_name='connection')
    client_ip = models.GenericIPAddressField()
    client_info = models.CharField(max_length=255, blank=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Активное подключение"
        verbose_name_plural = "Активные подключения"

    def __str__(self):
        return f"{self.token.token[:20]} -> {self.server.name}"

    def disconnect(self):
        self.is_active = False
        self.disconnected_at = timezone.now()
        self.save()
        if self.server:
            self.server.release()
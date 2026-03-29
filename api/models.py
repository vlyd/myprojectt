# api/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
import socket
import logging

logger = logging.getLogger(__name__)


class User(AbstractUser):
    """
    Кастомная модель пользователя с UUID
    """
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


class VPSServer(models.Model):
    """
    Модель для хранения данных VPS сервера
    """
    STATUS_CHOICES = [
        ('free', 'Свободен'),
        ('busy', 'Занят'),
        ('error', 'Ошибка'),
        ('maintenance', 'Обслуживание'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='free',
        verbose_name="Статус"
    )

    current_token = models.ForeignKey(
        'ProxyToken',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='using_server',
        verbose_name="Текущий токен"
    )

    current_connection = models.OneToOneField(
        'ActiveConnection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='server_connection',
        verbose_name="Активное подключение"
    )

    busy_since = models.DateTimeField(null=True, blank=True, verbose_name="Занят с")

    ip_address = models.GenericIPAddressField(
        verbose_name="IP адрес",
        default='192.168.56.105'
    )

    proxy_port = models.IntegerField(
        default=3128,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        verbose_name="Порт прокси"
    )

    proxy_username = models.CharField(
        max_length=50,
        default='username',
        verbose_name="Логин"
    )

    proxy_password = models.CharField(
        max_length=255,
        verbose_name="Пароль"
    )

    connection_method = models.CharField(
        max_length=100,
        default='HTTP-прокси с аутентификацией',
        verbose_name="Способ подключения"
    )

    last_checked = models.DateTimeField(null=True, blank=True)
    last_online = models.DateTimeField(null=True, blank=True)
    response_time_ms = models.IntegerField(default=0)

    total_connections = models.IntegerField(default=0, verbose_name="Всего подключений")
    total_time_seconds = models.IntegerField(default=0, verbose_name="Общее время работы (сек)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Прокси-сервер"
        verbose_name_plural = "Прокси-серверы"
        ordering = ['status', 'name']

    def __str__(self):
        status_icon = {
            'free': '🟢',
            'busy': '🔴',
            'error': '⚫',
            'maintenance': '🟡',
        }.get(self.status, '⚪')

        if self.status == 'busy' and self.current_token:
            return f"{status_icon} {self.name} - используется {self.current_token.token[:20]}..."
        return f"{status_icon} {self.name}"

    @property
    def is_available(self):
        return self.status == 'free'

    def get_connection_url(self):
        return f"http://{self.proxy_username}:{self.proxy_password}@{self.ip_address}:{self.proxy_port}"

    def assign_to_token(self, token, connection):
        if not self.is_available:
            return False

        self.status = 'busy'
        self.current_token = token
        self.current_connection = connection
        self.busy_since = timezone.now()
        self.total_connections += 1
        self.save()
        return True

    def release(self):
        if self.status == 'busy' and self.busy_since:
            time_used = (timezone.now() - self.busy_since).seconds
            self.total_time_seconds += time_used

        self.status = 'free'
        self.current_token = None
        self.current_connection = None
        self.busy_since = None
        self.save()

    def check_status(self):
        import time

        start = time.time()
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((str(self.ip_address), self.proxy_port))

            response_time = int((time.time() - start) * 1000)
            self.response_time_ms = response_time

            if result == 0:
                if self.status != 'busy':
                    self.status = 'free'
                self.last_online = timezone.now()
            else:
                if self.status != 'busy':
                    self.status = 'error'

        except socket.error as e:
            logger.error(f"Socket error checking server {self.name}: {e}")
            if self.status != 'busy':
                self.status = 'error'
        except Exception as e:
            logger.error(f"Unexpected error checking server {self.name}: {e}")
            if self.status != 'busy':
                self.status = 'error'
        finally:
            if sock:
                sock.close()
            self.last_checked = timezone.now()
            self.save()


class ProxyToken(models.Model):
    """
    Упрощенная модель для токенов доступа
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    traffic_limit_mb = models.IntegerField(default=1024)
    traffic_used_mb = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    current_connection = models.OneToOneField(
        'ActiveConnection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='token_connection'
    )

    class Meta:
        verbose_name = "Токен доступа"
        verbose_name_plural = "Токены доступа"

    def __str__(self):
        return f"{self.token[:20]}..."

    @property
    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at < timezone.now():
            return False
        if self.traffic_limit_mb > 0 and self.traffic_used_mb >= self.traffic_limit_mb:
            return False
        if self.current_connection:
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
        if self.current_connection:
            return "В сети"
        return "Доступен"

    def use_traffic(self, mb):
        self.traffic_used_mb += mb
        self.save()


class ActiveConnection(models.Model):
    """
    Модель для отслеживания активного подключения
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    token = models.OneToOneField(
        ProxyToken,
        on_delete=models.CASCADE,
        related_name='active_connection'
    )
    server = models.OneToOneField(
        VPSServer,
        on_delete=models.CASCADE,
        related_name='active_connection'
    )

    client_ip = models.GenericIPAddressField(verbose_name="IP клиента")
    client_info = models.CharField(max_length=255, blank=True, verbose_name="Информация о клиенте")

    connected_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)

    bytes_sent = models.BigIntegerField(default=0)
    bytes_received = models.BigIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Активное подключение"
        verbose_name_plural = "Активные подключения"

    def __str__(self):
        return f"{self.token.token[:20]}... -> {self.server.name}"

    def disconnect(self):
        self.is_active = False
        self.disconnected_at = timezone.now()
        self.save()

        if self.server:
            self.server.release()

        if self.token:
            self.token.current_connection = None
            self.token.save()


class EmailVerificationToken(models.Model):
    """
    Модель для токенов подтверждения email
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='verification_token'
    )
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "Токен подтверждения"
        verbose_name_plural = "Токены подтверждения"

    def __str__(self):
        return f"{self.user.email} - {self.token[:20]}..."

    @property
    def is_valid(self):
        return self.expires_at > timezone.now()
import uuid
from django.utils import timezone
import datetime
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailVerificationToken


def generate_verification_token(user):
    """
    Генерация уникального токена для подтверждения email
    """
    # Удаляем старый токен, если есть
    EmailVerificationToken.objects.filter(user=user).delete()

    # Создаем новый токен
    token = uuid.uuid4().hex + uuid.uuid4().hex  # 64 символа
    expires_at = timezone.now() + datetime.timedelta(hours=24)  # 24 часа

    verification_token = EmailVerificationToken.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )

    return token


def send_verification_email(user, token):
    """
    Отправка email с ссылкой для подтверждения
    """
    # Ссылка для подтверждения
    verification_link = f"http://localhost:5173/verify-email/{token}/"

    # Тема письма
    subject = "Подтверждение email - Proxy Service"

    # Текст письма (простая версия)
    message = f"""
Здравствуйте, {user.username}!

Спасибо за регистрацию в Proxy Service.

Для подтверждения email перейдите по ссылке:
{verification_link}

Ссылка действительна 24 часа.

Если вы не регистрировались, проигнорируйте это письмо.

"""

    # Отправка письма
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    print(f"📧 Письмо отправлено на {user.email}")
    print(f"🔗 Ссылка: {verification_link}")


def resend_verification_email(user):
    """
    Повторная отправка письма с подтверждением
    """
    token = generate_verification_token(user)
    send_verification_email(user, token)
from django.urls import path
from . import views

urlpatterns = [
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('me/', views.me, name='me'),

    # Подтверждение email
    path('verify-email/<str:token>/', views.verify_email, name='verify-email'),
    path('resend-verification/', views.resend_verification, name='resend-verification'),

    # Управление токенами
    path('tokens/create/', views.create_token, name='create-token'),
    path('token/<str:token_str>/status/', views.check_token_status, name='token-status'),

    # Прокси-серверы
    path('servers/', views.list_servers, name='list-servers'),

    # Подключения
    path('connect/', views.connect_by_token, name='connect'),
    path('disconnect/', views.disconnect, name='disconnect'),
]
# api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import uuid
import datetime
from .models import User, ProxyToken, VPSServer, ActiveConnection
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ProxyTokenSerializer, VPSServerSerializer, ActiveConnectionSerializer
)


# ============= АУТЕНТИФИКАЦИЯ =============

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Регистрация нового пользователя"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'success': True,
            'message': 'Пользователь успешно зарегистрирован',
            'user': UserSerializer(user).data
        }, status=201)
    return Response(serializer.errors, status=400)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Авторизация пользователя"""
    serializer = LoginSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        user = serializer.validated_data['user']
        auth_login(request, user)

        return Response({
            'success': True,
            'message': 'Успешный вход',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'phone': getattr(user, 'phone', ''),
                'balance': float(getattr(user, 'balance', 0)),
                'is_verified': getattr(user, 'is_verified', False),
            }
        }, status=200)

    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Получить информацию о текущем пользователе"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# ============= УПРАВЛЕНИЕ ТОКЕНАМИ =============

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_token(request):
    """Создать новый токен"""
    try:
        token_str = uuid.uuid4().hex
        expires_at = timezone.now() + datetime.timedelta(days=30)

        token = ProxyToken.objects.create(
            token=token_str,
            expires_at=expires_at,
            traffic_limit_mb=1024,
            is_active=True
        )

        return Response({'token': token.token}, status=201)

    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_token_status(request, token_str):
    """Проверить статус токена"""
    try:
        token = ProxyToken.objects.get(token=token_str)

        # Проверяем наличие активного подключения
        is_connected = ActiveConnection.objects.filter(token=token, is_active=True).exists()

        return Response({
            'is_valid': token.is_valid,
            'status': token.get_status_display,
            'expires_at': token.expires_at,
            'traffic_limit_mb': token.traffic_limit_mb,
            'traffic_used_mb': token.traffic_used_mb,
            'is_connected': is_connected
        })

    except ProxyToken.DoesNotExist:
        return Response({
            'is_valid': False,
            'message': 'Токен не найден'
        }, status=404)


# ============= ПРОКСИ-СЕРВЕРЫ =============

@api_view(['GET'])
@permission_classes([AllowAny])
def list_servers(request):
    """Получить список всех прокси-серверов"""
    try:
        servers = VPSServer.objects.all()
        data = []
        for server in servers:
            data.append({
                'id': str(server.id),
                'name': server.name,
                'ip_address': server.ip_address,
                'proxy_port': server.proxy_port,
                'status': server.status,
                'is_available': server.status == 'free'
            })
        return Response(data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# ============= ПОДКЛЮЧЕНИЯ =============

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def connect_by_token(request):
    """Подключение к прокси по токену"""
    try:
        token_str = request.data.get('token')
        client_info = request.data.get('client_info', '')
        client_ip = request.META.get('REMOTE_ADDR', '0.0.0.0')

        if not token_str:
            return Response({'error': 'Токен не указан'}, status=400)

        token = ProxyToken.objects.get(token=token_str)

        if not token.is_valid:
            return Response({'error': 'Токен недействителен'}, status=401)

        # Проверяем, не используется ли токен
        if ActiveConnection.objects.filter(token=token, is_active=True).exists():
            return Response({'error': 'Токен уже используется'}, status=401)

        # Ищем свободный сервер
        server = VPSServer.objects.filter(status='free').first()

        if not server:
            return Response({'error': 'Нет свободных серверов'}, status=503)

        # Удаляем старую запись для этого сервера (чтобы избежать UNIQUE constraint)
        ActiveConnection.objects.filter(server=server).delete()

        # Создаем новое подключение
        connection = ActiveConnection.objects.create(
            token=token,
            server=server,
            client_ip=client_ip,
            client_info=client_info,
            is_active=True
        )

        # Занимаем сервер
        server.status = 'busy'
        server.busy_since = timezone.now()
        server.total_connections += 1
        server.save()

        return Response({
            'success': True,
            'message': f'Подключено к серверу {server.name}',
            'connection_id': str(connection.id),
            'proxy': {
                'host': server.ip_address,
                'port': server.proxy_port,
                'username': server.proxy_username,
                'password': server.proxy_password,
                'type': 'http',
                'url': f'http://{server.proxy_username}:{server.proxy_password}@{server.ip_address}:{server.proxy_port}'
            },
            'server': {
                'id': str(server.id),
                'name': server.name,
                'ip_address': server.ip_address,
                'port': server.proxy_port,
                'response_time_ms': server.response_time_ms
            },
            'token_info': {
                'token': token.token,
                'expires_at': token.expires_at.isoformat(),
                'traffic_limit_mb': token.traffic_limit_mb,
                'traffic_used_mb': token.traffic_used_mb,
                'traffic_left_mb': token.traffic_limit_mb - token.traffic_used_mb,
                'status': token.get_status_display
            }
        }, status=200)

    except ProxyToken.DoesNotExist:
        return Response({'error': 'Токен не найден'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def disconnect(request):
    """Отключение от прокси"""
    try:
        connection_id = request.data.get('connection_id')
        token_str = request.data.get('token')

        if connection_id:
            connection = ActiveConnection.objects.get(id=connection_id, is_active=True)
        elif token_str:
            token = ProxyToken.objects.get(token=token_str)
            connection = ActiveConnection.objects.filter(token=token, is_active=True).first()
            if not connection:
                return Response({'error': 'Нет активного подключения для этого токена'}, status=404)
        else:
            return Response({'error': 'Не указан connection_id или token'}, status=400)

        # Отключаем
        connection.is_active = False
        connection.disconnected_at = timezone.now()
        connection.save()

        # Освобождаем сервер
        server = connection.server
        server.status = 'free'
        server.busy_since = None
        server.save()

        return Response({'success': True, 'message': 'Отключено'}, status=200)

    except ActiveConnection.DoesNotExist:
        return Response({'error': 'Подключение не найдено'}, status=404)
    except ProxyToken.DoesNotExist:
        return Response({'error': 'Токен не найден'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
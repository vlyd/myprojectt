from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, VPSServer, ProxyToken, ActiveConnection


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 'phone']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            phone=validated_data.get('phone', '')
        )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Неверный email или пароль")
            if not user.is_active:
                raise serializers.ValidationError("Пользователь неактивен")
        else:
            raise serializers.ValidationError("Необходимо указать email и пароль")

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'balance', 'is_verified', 'created_at']
        read_only_fields = ['id', 'balance', 'is_verified', 'created_at']


class ProxyTokenSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ProxyToken
        fields = ['id', 'token', 'created_at', 'expires_at', 'traffic_limit_mb',
                  'traffic_used_mb', 'is_active', 'status']
        read_only_fields = ['id', 'created_at']


class VPSServerSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)
    connection_url = serializers.CharField(read_only=True)

    class Meta:
        model = VPSServer
        fields = [
            'id', 'name', 'description', 'status', 'ip_address', 'proxy_port',
            'proxy_username', 'proxy_password', 'connection_method',
            'is_available', 'connection_url', 'response_time_ms',
            'total_connections', 'total_time_seconds'
        ]
        read_only_fields = ['id', 'response_time_ms', 'total_connections', 'total_time_seconds']


class ActiveConnectionSerializer(serializers.ModelSerializer):
    token_info = ProxyTokenSerializer(source='token', read_only=True)
    server_info = VPSServerSerializer(source='server', read_only=True)

    class Meta:
        model = ActiveConnection
        fields = [
            'id', 'token', 'server', 'token_info', 'server_info',
            'client_ip', 'client_info', 'connected_at', 'last_activity',
            'bytes_sent', 'bytes_received', 'is_active'
        ]
        read_only_fields = ['id', 'connected_at', 'last_activity']


# ============= ДОБАВИТЬ ЭТОТ КЛАСС =============
class CreateTokenSerializer(serializers.Serializer):
    """
    Сериализатор для создания токена (упрощенный)
    Не требует никаких параметров
    """
    pass
# api/permissions.py
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsTokenOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        token_id = view.kwargs.get('pk')
        if token_id:
            from .models import ProxyToken
            try:
                token = ProxyToken.objects.get(id=token_id)
                return token.user == request.user
            except ProxyToken.DoesNotExist:
                return False
        return True
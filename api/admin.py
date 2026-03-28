from django.contrib import admin
from .models import VPSServer

@admin.register(VPSServer)
class VPSServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'proxy_port', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'ip_address']
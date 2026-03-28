# api/management/commands/server_status.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import VPSServer, ProxyToken


class Command(BaseCommand):
    help = 'Показать статус серверов и подключений'

    def handle(self, *args, **options):
        self.stdout.write("\n=== СТАТУС СЕРВЕРОВ ===\n")

        servers = VPSServer.objects.all()
        for server in servers:
            if server.status == 'busy' and server.current_user:
                time_used = (timezone.now() - server.busy_since).seconds // 60 if server.busy_since else 0
                self.stdout.write(
                    f"{server} - занят {time_used} мин"
                )
            else:
                self.stdout.write(str(server))

        self.stdout.write("\n=== СТАТУС ТОКЕНОВ ===\n")

        tokens = ProxyToken.objects.all()
        for token in tokens:
            self.stdout.write(f"{token}")
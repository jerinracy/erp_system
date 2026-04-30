from django.core.management.base import BaseCommand

from apps.integrations.services.retry_service import retry_failed_webhooks


class Command(BaseCommand):
    help = "Retry failed webhooks"

    def handle(self, *args, **kwargs):
        retry_failed_webhooks()
        self.stdout.write("Retry completed")

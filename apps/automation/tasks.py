from celery import shared_task

from apps.automation.models import Event
from apps.automation.services.rule_engine import process_event


@shared_task(bind=True, max_retries=3)
def process_event_task(self, event_id):
    try:
        event = Event.objects.get(id=event_id)
        process_event(event)

    except Exception as e:
        raise self.retry(exc=e, countdown=10)

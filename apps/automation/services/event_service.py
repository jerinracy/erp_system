from apps.automation.models import Event
from apps.automation.tasks import process_event_task


def create_event(event_type, payload, tenant):
    event = Event.objects.create(tenant=tenant, event_type=event_type, payload=payload)

    # 🔥 ASYNC (no blocking)
    process_event_task.delay(event.id)

    return event

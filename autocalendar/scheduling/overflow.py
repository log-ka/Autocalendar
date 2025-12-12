from datetime import timedelta

from .types import Event


def handle_overflow(event: Event) -> Event:
    return Event(
        title=event.title,
        date=event.date + timedelta(days=1),
        time=None,
        duration=event.duration,
        priority=event.priority,
    )

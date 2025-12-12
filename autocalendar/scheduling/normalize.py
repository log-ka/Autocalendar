from .types import Event


DEFAULT_DURATION = 60  # минут


def normalize_duration(event: Event) -> Event:
    if event.duration <= 0:
        raise ValueError("Duration must be positive")

    return event

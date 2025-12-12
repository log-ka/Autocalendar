from typing import List

from .types import Event


def sort_flexible_events(events: List[Event]) -> List[Event]:
    return sorted(
        events,
        key=lambda e: (-e.priority, -e.duration)
    )

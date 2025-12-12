from collections import defaultdict, deque
from datetime import date, time as time_type
from typing import List

from .types import Event, ScheduledEvent
from .constraints import WorkDay
from .slots import build_free_slots, can_fit, consume
from .sorter import sort_flexible_events
from .overflow import handle_overflow


def autoschedule(
    events: List[Event],
    work_day: WorkDay
) -> List[ScheduledEvent]:

    events_by_date: dict[date, list[Event]] = defaultdict(list)
    for event in events:
        events_by_date[event.date].append(event)

    queue = deque(sorted(events_by_date.items(), key=lambda x: x[0]))
    result: List[ScheduledEvent] = []

    while queue:
        current_date, day_events = queue.popleft()

        fixed: List[ScheduledEvent] = []
        flexible: List[Event] = []

        for event in day_events:
            if event.time is not None:
                fixed.append(
                    ScheduledEvent(
                        title=event.title,
                        date=event.date,
                        time=event.time,
                        duration=event.duration,
                        priority=event.priority,
                    )
                )
            else:
                flexible.append(event)

        free_slots = build_free_slots(fixed, work_day)
        flexible = sort_flexible_events(flexible)

        overflow_events: List[Event] = []

        for event in flexible:
            placed = False
            for i, slot in enumerate(free_slots):
                if can_fit(slot, event.duration):
                    scheduled = ScheduledEvent(
                        title=event.title,
                        date=current_date,
                        time=slot.start,
                        duration=event.duration,
                        priority=event.priority,
                    )
                    result.append(scheduled)

                    new_slot = consume(slot, event.duration)
                    if new_slot is None:
                        free_slots.pop(i)
                    else:
                        free_slots[i] = new_slot

                    placed = True
                    break

            if not placed:
                overflow_events.append(handle_overflow(event))

        result.extend(fixed)

        if overflow_events:
            next_date = overflow_events[0].date
            events_by_date[next_date].extend(overflow_events)
            queue.append((next_date, events_by_date[next_date]))

    return result

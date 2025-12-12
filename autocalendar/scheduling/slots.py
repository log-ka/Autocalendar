from datetime import time
from typing import List

from .types import TimeSlot, ScheduledEvent
from .constraints import WorkDay


def _to_minutes(t: time) -> int:
    return t.hour * 60 + t.minute


def _from_minutes(m: int) -> time:
    return time(m // 60, m % 60)


def build_free_slots(
    fixed_events: List[ScheduledEvent],
    work_day: WorkDay
) -> List[TimeSlot]:
    if not fixed_events:
        return [TimeSlot(work_day.start, work_day.end)]

    fixed_events = sorted(fixed_events, key=lambda e: _to_minutes(e.time))
    slots: List[TimeSlot] = []

    cursor = _to_minutes(work_day.start)

    for event in fixed_events:
        start = _to_minutes(event.time)
        end = start + event.duration

        if cursor < start:
            slots.append(
                TimeSlot(
                    start=_from_minutes(cursor),
                    end=_from_minutes(start)
                )
            )
        cursor = max(cursor, end)

    work_end = _to_minutes(work_day.end)
    if cursor < work_end:
        slots.append(
            TimeSlot(
                start=_from_minutes(cursor),
                end=_from_minutes(work_end)
            )
        )

    return slots


def can_fit(slot: TimeSlot, duration: int) -> bool:
    return slot.duration_minutes() >= duration


def consume(slot: TimeSlot, duration: int) -> TimeSlot | None:
    new_start = _to_minutes(slot.start) + duration
    end = _to_minutes(slot.end)

    if new_start >= end:
        return None

    return TimeSlot(
        start=_from_minutes(new_start),
        end=slot.end
    )

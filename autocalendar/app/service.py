from datetime import datetime, time
from zoneinfo import ZoneInfo
from typing import Iterable, List

from autocalendar.parsing import parse_event_title
from autocalendar.scheduling import Event, WorkDay, autoschedule
from autocalendar.scheduling.normalize import DEFAULT_DURATION
from autocalendar.inbox import Inbox


def build_schedule(
    raw_inputs: Iterable[str],
    *,
    now: datetime,
    tz: ZoneInfo,
    inbox: Inbox,
    work_day: WorkDay,
    language: str = "ru",
) -> List[Event]:
    parsed = [
        parse_event_title(
            raw,
            now=now,
            tz=tz,
            language=language,
        )
        for raw in raw_inputs
    ]

    events: list[Event] = []

    for p in parsed:
        if p.d is None:
            inbox.add(p.title)
            continue

        events.append(
            Event(
                title=p.title,
                date=p.d,
                time=p.t,
                duration=p.duration or DEFAULT_DURATION,
                priority=1,
            )
        )

    return autoschedule(events, work_day)

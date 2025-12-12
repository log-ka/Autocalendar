from datetime import time
from zoneinfo import ZoneInfo

from datetime import datetime, time as time_type

from autocalendar.parsing import parse_event_title
from autocalendar.scheduling import Event, WorkDay, autoschedule
from autocalendar.scheduling.normalize import DEFAULT_DURATION

from autocalendar.inbox import Inbox

inbox = Inbox()

TZ = ZoneInfo("Europe/Moscow")


def parsed_to_event(parsed, inbox: Inbox):

    if parsed.d is None:
        inbox.add(parsed.title)
        return None

    return Event(
        title=parsed.title,
        date=parsed.d,
        time=parsed.t,
        duration=DEFAULT_DURATION,
        priority=1,
    )


def main():
    user_input = input()
    raw_inputs = []

    while user_input != "q":
        raw_inputs.append(user_input)
        user_input = input()

    now = datetime.now(TZ)

    parsed_events = [
        parse_event_title(
            raw,
            now=now,
            tz=TZ,
            language="ru",
        )
        for raw in raw_inputs
    ]

    events = [
        e for e in (
            parsed_to_event(p, inbox)
            for p in parsed_events
        )
        if e is not None
    ]

    work_day = WorkDay(
        start=time(9, 0),
        end=time(18, 0),
    )

    scheduled = autoschedule(events, work_day)

    def sort_key(event):
        return (
            event.date,
            event.time or time.max,
            -event.priority,
            event.title,
        )

    for e in sorted(scheduled, key=sort_key):
        print(f"{e.date} {e.time} — {e.title}")

    if not inbox.is_empty():
        print("\n📥 Inbox:")
        for item in sorted(inbox.list(), key=lambda x: x.created_at):
            print(f"- {item.title}")


if __name__ == "__main__":
    main()

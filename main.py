from datetime import datetime, time
from zoneinfo import ZoneInfo

from autocalendar.app.service import build_schedule
from autocalendar.inbox import Inbox
from autocalendar.scheduling import WorkDay


def main():
    tz = ZoneInfo("Europe/Moscow")
    inbox = Inbox()

    print("=" * 5 ,"Autocalendar v1.1", "=" * 5)
    print('Введите названия событий, когда закончите введите "q"')

    raw_inputs = []
    while True:
        user_input = input()
        if user_input == "q":
            break
        raw_inputs.append(user_input)

    now = datetime.now(tz)

    work_day = WorkDay(
        start=time(9, 0),
        end=time(18, 0),
    )

    scheduled = build_schedule(
        raw_inputs,
        now=now,
        tz=tz,
        inbox=inbox,
        work_day=work_day,
    )

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

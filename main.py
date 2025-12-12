from datetime import datetime

from autocalendar.config import USER_TIMEZONE
from autocalendar.parsing import parse_event_title

def main() -> None:
    now = datetime.now(USER_TIMEZONE)

    s = "Созвон с Климом сегодня 18:00"
    parsed = parse_event_title(s, now=now, tz=USER_TIMEZONE)
    print(parsed)

if __name__ == "__main__":
    main()

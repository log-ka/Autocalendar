from autocalendar.parsing.normalize import normalize_text
from autocalendar.parsing.datetime_extractor import extract_datetime
from autocalendar.parsing.duration_extractor import extract_duration
from autocalendar.parsing.money_extractor import extract_money
from autocalendar.parsing.cleanup import cleanup_title
from autocalendar.parsing.types import ParsedEvent


def parse_event_title(raw: str, *, now, tz, language="ru") -> ParsedEvent:
    text = normalize_text(raw)

    dt, text, explicit_time = extract_datetime(
        text,
        now=now,
        tz=tz,
        language=language,
    )

    duration, explicit_duration, text = extract_duration(
        text,
        raw_text=raw,
        dt=dt,
        explicit_time=explicit_time,
    )

    price, text = extract_money(text)

    title = cleanup_title(text)

    return ParsedEvent(
        raw=raw,
        title=title,
        dt=dt,
        d=dt.date() if dt else None,
        t=dt.time() if (dt and explicit_time) else None,  # 🔑 КЛЮЧ
        price=price,
        duration=duration,
        explicit_duration=explicit_duration,
        leftovers=text,
    )

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

    duration, explicit_duration, text = extract_duration(text)

    # If duration wasn't explicitly found, infer it from a time range
    # in the original raw text like "10:00-11:30" for fixed events.
    if duration is None and dt is not None and explicit_time:
        import re

        m = re.search(r"\b(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})\b", raw)
        if m:
            def _to_minutes(s: str) -> int:
                h, mm = map(int, s.split(":"))
                return h * 60 + mm

            start_min = _to_minutes(m.group(1))
            end_min = _to_minutes(m.group(2))
            if end_min <= start_min:
                end_min += 24 * 60

            duration = end_min - start_min

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

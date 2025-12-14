import re
from typing import Optional, Tuple


_TIME_RANGE_RE = re.compile(
    r'(?P<start>\d{1,2}:\d{2})\s*[-–]\s*(?P<end>\d{1,2}:\d{2})'
)

_HOURS_RE = re.compile(
    r'(?P<value>\d+(?:[.,]\d+)?)\s*(?:ч|час|часа|часов)\b',
    re.IGNORECASE
)

_MINUTES_RE = re.compile(
    r'(?P<value>\d+)\s*(?:м|мин|минута|минуты|минут)\b',
    re.IGNORECASE
)


def _to_minutes(time_str: str) -> Optional[int]:
    try:
        h, m = map(int, time_str.split(":"))
        return h * 60 + m
    except Exception:
        return None


def extract_duration(
    text: str,
    *,
    raw_text: str | None = None,
     dt=None,
     explicit_time: bool = False,
) -> Tuple[Optional[int], bool, str]:
    """
    Returns:
        duration_minutes | None
        explicit_duration
        cleaned_text
    """

    if not isinstance(text, str):
        raise TypeError(f"extract_duration expected str, got {type(text)}")

    # 1. time range: 10:00-11:30
    if explicit_time and dt:
        source = raw_text if raw_text is not None else text
        m = _TIME_RANGE_RE.search(source)
        if m:
            start = _to_minutes(m.group("start"))
            end = _to_minutes(m.group("end"))

            if start is not None and end is not None:
                if end <= start:
                    end += 24 * 60

                duration = end - start
                cleaned = (text[:m.start()] + text[m.end():]).strip()
                return duration, True, cleaned

    # 2. hours
    m = _HOURS_RE.search(text)
    if m:
        value = float(m.group("value").replace(",", "."))
        cleaned = (text[:m.start()] + text[m.end():]).strip()
        return int(round(value * 60)), True, cleaned

    # 3. minutes
    m = _MINUTES_RE.search(text)
    if m:
        value = int(m.group("value"))
        cleaned = (text[:m.start()] + text[m.end():]).strip()
        return value, True, cleaned

    # 4. nothing found
    return None, False, text

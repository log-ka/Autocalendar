from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from .types import ParsedEvent
from .normalize import normalize_text
from .datetime_extractor import extract_datetime
from .money_extractor import extract_money
from .cleanup import cleanup_title


def parse_event_title(
    raw_text: str,
    *,
    now: datetime,
    tz: ZoneInfo,
    language: str = "ru",
) -> ParsedEvent:
    """
    Главная “точка входа” парсера.
    Внутри — конвейер: normalize -> datetime -> money -> cleanup.
    """
    raw = raw_text
    text = normalize_text(raw_text)

    price, text = extract_money(text)
    dt, text = extract_datetime(text, now=now, tz=tz, language=language)

    title = cleanup_title(text)

    d = dt.date() if dt else None
    # timetz() сохраняет tzinfo; но нам в ParsedEvent обычно нужно “чистое” время
    t = dt.timetz().replace(tzinfo=None) if dt else None

    return ParsedEvent(
        raw=raw,
        title=title,
        dt=dt,
        d=d,
        t=t,
        price=price,
        leftovers=text,
    )

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

from dateparser.search import search_dates


_TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")
_TIME_PATTERN = re.compile(r"\b\d{1,2}:\d{2}\b")
_DATE_DDMM_RE = re.compile(r"\b(?P<d>[0-3]?\d)\.(?P<m>[01]?\d)\b")

_DATE_HINT_RE = re.compile(
    r"\b(сегодня|завтра|послезавтра|\d{1,2}[./]\d{1,2})\b",
    re.IGNORECASE,
)


def extract_datetime(
    text: str,
    *,
    now: datetime,
    tz: ZoneInfo,
    language: str = "ru",
) -> Tuple[Optional[datetime], str, bool]:
    """
    Returns:
        dt: datetime | None
        cleaned_text: str
        explicit_time: bool
    """

    # --------------------------------------------------
    # 0. TIME RANGE WITHOUT DATE (e.g. "10:00-11:30")
    # --------------------------------------------------
    range_match = re.search(r"\b(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})\b", text)
    has_date_hint = _DATE_HINT_RE.search(text)

    if range_match and not has_date_hint:
        hh = int(range_match.group(1).split(":")[0])
        mm = int(range_match.group(1).split(":")[1])

        base_date = now.date()
        if (hh, mm) <= (now.hour, now.minute):
            base_date += timedelta(days=1)

        dt = datetime(
            base_date.year,
            base_date.month,
            base_date.day,
            hh,
            mm,
            tzinfo=tz,
        )

        cleaned = text.replace(range_match.group(0), "", 1)
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

        return dt, cleaned, True

    if not isinstance(text, str):
        raise TypeError(f"extract_datetime expected str, got {type(text)}")

    # --------------------------------------------------
    # 1. TIME WITHOUT DATE (e.g. "10:00")
    # --------------------------------------------------
    m_time = _TIME_RE.search(text)
    has_date_hint = _DATE_HINT_RE.search(text)

    if m_time and not has_date_hint:
        hh = int(m_time.group(1))
        mm = int(m_time.group(2))

        base_date = now.date()
        if (hh, mm) <= (now.hour, now.minute):
            base_date += timedelta(days=1)

        dt = datetime(
            base_date.year,
            base_date.month,
            base_date.day,
            hh,
            mm,
            tzinfo=tz,
        )

        cleaned = _TIME_RE.sub("", text, count=1)
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

        return dt, cleaned, True

    # --------------------------------------------------
    # 2. EXPLICIT DD.MM (optional time)
    # --------------------------------------------------
    m_date = _DATE_DDMM_RE.search(text)
    if m_date:
        day = int(m_date.group("d"))
        month = int(m_date.group("m"))
        year = now.year
        if (month, day) < (now.month, now.day):
            year += 1

        cleaned = text[:m_date.start()] + text[m_date.end():]

        m_time = _TIME_RE.search(cleaned)
        if m_time:
            hh = int(m_time.group(1))
            mm = int(m_time.group(2))
            explicit_time = True
            cleaned = _TIME_RE.sub("", cleaned, count=1)
        else:
            hh = 0
            mm = 0
            explicit_time = False

        dt = datetime(year, month, day, hh, mm, tzinfo=tz)
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

        return dt, cleaned, explicit_time

    if not _DATE_HINT_RE.search(text):
        return None, text, False

    # --------------------------------------------------
    # 3. RELATIVE DATES via dateparser (NO TIME TRUST)
    # --------------------------------------------------
    settings = {
        "RELATIVE_BASE": now,
        "TIMEZONE": tz.key,
        "TO_TIMEZONE": tz.key,
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DATES_FROM": "future",
        "DATE_ORDER": "DMY",
    }

    found = search_dates(text, languages=[language], settings=settings)
    if not found:
        return None, text, False

    explicit_time = False
    dt: Optional[datetime] = None
    matched_text: Optional[str] = None

    for text_part, candidate_dt in found:
        if _TIME_PATTERN.search(text_part):
            explicit_time = True
            dt = candidate_dt
            matched_text = text_part
            break

    if dt is None:
        matched_text, candidate_dt = found[0]
        dt = datetime(
            candidate_dt.year,
            candidate_dt.month,
            candidate_dt.day,
            0,
            0,
            tzinfo=tz,
        )

    cleaned = text.replace(matched_text, "", 1)
    cleaned = _TIME_RE.sub("", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

    return dt, cleaned, explicit_time

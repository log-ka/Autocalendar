from __future__ import annotations

import re
from datetime import datetime, timedelta, time as dtime
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

from dateparser.search import search_dates

# NOTE: dot removed to avoid matching dates like "13.12" as time "13:12"
_TIME_RE = re.compile(r"\b([01]?\d|2[0-3])[: ]([0-5]\d)\b")
_DATE_DDMM_RE = re.compile(r"\b(?P<d>[0-3]?\d)\.(?P<m>[01]?\d)\b")


def extract_datetime(
    text: str,
    *,
    now: datetime,
    tz: ZoneInfo,
    language: str = "ru",
) -> Tuple[Optional[datetime], str]:
    settings = {
        "RELATIVE_BASE": now,
        "TIMEZONE": tz.key,
        "TO_TIMEZONE": tz.key,
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DATES_FROM": "future",
        "DATE_ORDER": "DMY",
    }

    # --- 1) Explicit DD.MM (with optional time) ---
    m_date = _DATE_DDMM_RE.search(text)

    if m_date:
        day = int(m_date.group("d"))
        month = int(m_date.group("m"))
        year = now.year

        # если дата уже прошла — берём следующий год
        if (month, day) < (now.month, now.day):
            year += 1

        # 1) Сначала убираем дату из текста (чтобы время искалось корректно)
        cleaned = text
        cleaned = cleaned[:m_date.start()] + cleaned[m_date.end():]

        # 2) Теперь ищем время уже на cleaned (там нет "13.12")
        m_time = _TIME_RE.search(cleaned)

        if m_time:
            hh = int(m_time.group(1))
            mm = int(m_time.group(2))
            dt = datetime(year, month, day, hh, mm, tzinfo=tz)

            # удаляем только одно совпадение времени
            cleaned = _TIME_RE.sub("", cleaned, count=1)
        else:
            dt = datetime(year, month, day, 0, 0, tzinfo=tz)

        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
        return dt, cleaned

    # --- 2) dateparser for relative dates / weekdays ---
    found = search_dates(text, languages=[language], settings=settings)

    dt: Optional[datetime] = None
    cleaned = text

    if found:
        matched_text, matched_dt = max(found, key=lambda x: len(x[0] or ""))
        dt = matched_dt

        cleaned = re.sub(re.escape(matched_text), "", cleaned, count=1).strip()
        cleaned = _TIME_RE.sub("", cleaned).strip()
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
        return dt, cleaned

    # --- 3) Fallback: time-only ---
    m_time = _TIME_RE.search(cleaned)
    if m_time:
        hh = int(m_time.group(1))
        mm = int(m_time.group(2))
        t = dtime(hh, mm)

        base_date = now.date()
        if (hh, mm) < (now.hour, now.minute):
            base_date = base_date + timedelta(days=1)

        dt = datetime(base_date.year, base_date.month, base_date.day, hh, mm, tzinfo=tz)

        cleaned = cleaned[:m_time.start()] + cleaned[m_time.end():]
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

    return dt, cleaned

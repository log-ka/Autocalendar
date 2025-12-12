import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from autocalendar.parsing.datetime_extractor import extract_datetime
from autocalendar.parsing.duration_extractor import extract_duration
from autocalendar.parsing.parser import parse_event_title


TZ = ZoneInfo("Europe/Moscow")
NOW = datetime(2025, 12, 12, 12, 0, tzinfo=TZ)


# --------------------------------------------------
# extract_datetime
# --------------------------------------------------

def test_relative_date_without_time():
    dt, text, explicit = extract_datetime(
        "Задача завтра",
        now=NOW,
        tz=TZ,
        language="ru",
    )

    assert dt is not None
    assert dt.date().day == 13
    assert explicit is False
    assert text == "Задача"


def test_time_without_date_future_today():
    dt, text, explicit = extract_datetime(
        "Задача 15:00",
        now=NOW,
        tz=TZ,
        language="ru",
    )

    assert dt.date() == NOW.date()
    assert dt.time().hour == 15
    assert explicit is True
    assert text == "Задача"


def test_time_without_date_past_goes_to_tomorrow():
    dt, text, explicit = extract_datetime(
        "Задача 10:00",
        now=NOW,
        tz=TZ,
        language="ru",
    )

    assert dt.date().day == 13
    assert dt.time().hour == 10
    assert explicit is True


def test_time_range_without_date():
    dt, text, explicit = extract_datetime(
        "Задача 10:00-11:30",
        now=NOW,
        tz=TZ,
        language="ru",
    )

    assert dt.date().day == 13
    assert dt.time().hour == 10
    assert explicit is True
    assert text == "Задача"


# --------------------------------------------------
# extract_duration
# --------------------------------------------------

def test_duration_minutes():
    duration, explicit, text = extract_duration("Задача 45 мин")

    assert duration == 45
    assert explicit is True
    assert text == "Задача"


def test_duration_hours_float():
    duration, explicit, text = extract_duration("Задача 1.5 часа")

    assert duration == 90
    assert explicit is True
    assert text == "Задача"


def test_duration_not_found():
    duration, explicit, text = extract_duration("Задача")

    assert duration is None
    assert explicit is False
    assert text == "Задача"


# --------------------------------------------------
# parse_event_title (end-to-end)
# --------------------------------------------------

def test_parse_tomorrow_flexible():
    parsed = parse_event_title(
        "Задача завтра",
        now=NOW,
        tz=TZ,
        language="ru",
    )

    assert parsed.d is not None
    assert parsed.t is None
    assert parsed.duration is None


def test_parse_duration_only_goes_to_inbox():
    parsed = parse_event_title(
        "Задача 45 мин",
        now=NOW,
        tz=TZ,
        language="ru",
    )

    assert parsed.d is None
    assert parsed.duration == 45
    assert parsed.t is None


def test_parse_time_range_fixed_event():
    parsed = parse_event_title(
        "Задача 10:00-11:30",
        now=NOW,
        tz=TZ,
        language="ru",
    )

    assert parsed.d is not None
    assert parsed.t is not None
    assert parsed.t.hour == 10
    assert parsed.duration == 90

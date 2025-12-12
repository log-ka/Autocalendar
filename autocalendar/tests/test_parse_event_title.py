from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, time
from typing import Any

from autocalendar.config import USER_TIMEZONE
from autocalendar.parsing import parse_event_title


# ---------------------------
# Test model
# ---------------------------

@dataclass(frozen=True)
class Case:
    name: str
    raw: str
    now: datetime

    exp_title: str | None = None
    exp_d: date | None = None
    exp_t: time | None = None
    exp_dt: datetime | None = None

    # If dt exists, ensure tzinfo key equals this (ZoneInfo.key usually)
    exp_tz_key: str | None = "Europe/Moscow"

    # Substrings that must NOT remain in leftovers
    leftovers_must_not_contain: tuple[str, ...] = ()

    # Price checks are intentionally “soft” because your MoneyValue shape may differ.
    price_should_exist: bool | None = None
    exp_price_amount: int | float | None = None
    exp_price_currency: str | None = None


# ---------------------------
# Helpers
# ---------------------------

def _tz_key(dt: datetime | None) -> str | None:
    if dt is None or dt.tzinfo is None:
        return None
    return getattr(dt.tzinfo, "key", str(dt.tzinfo))


def _getattr(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default)


def _price_amount(price: Any) -> int | float | None:
    if price is None:
        return None
    for attr in ("amount", "value", "sum"):
        if hasattr(price, attr):
            return getattr(price, attr)
    # handle nested patterns if needed
    if hasattr(price, "amount") and hasattr(price.amount, "value"):
        return price.amount.value
    return None


def _price_currency(price: Any) -> str | None:
    if price is None:
        return None
    for attr in ("currency", "cur"):
        if hasattr(price, attr):
            return getattr(price, attr)
    if hasattr(price, "currency") and hasattr(price.currency, "code"):
        return price.currency.code
    return None


def _fail(lines: list[str], msg: str) -> None:
    lines.append(msg)


def _assert_eq(lines: list[str], field: str, got: Any, exp: Any) -> None:
    if got != exp:
        _fail(lines, f"{field}: expected={exp!r} got={got!r}")


def _assert_not_contains(lines: list[str], field: str, text: str | None, needle: str) -> None:
    hay = text or ""
    if needle in hay:
        _fail(lines, f"{field}: must NOT contain {needle!r}, got={hay!r}")


# ---------------------------
# Runner
# ---------------------------

def run_case(c: Case) -> list[str]:
    errs: list[str] = []

    parsed = parse_event_title(c.raw, now=c.now, tz=USER_TIMEZONE)

    # Required attributes
    for attr in ("raw", "title", "dt", "d", "t", "leftovers", "price"):
        if not hasattr(parsed, attr):
            _fail(errs, f"missing attribute parsed.{attr}")

    # Field expectations
    if c.exp_title is not None:
        _assert_eq(errs, "title", _getattr(parsed, "title"), c.exp_title)

    if c.exp_d is not None:
        _assert_eq(errs, "d", _getattr(parsed, "d"), c.exp_d)

    if c.exp_t is not None:
        _assert_eq(errs, "t", _getattr(parsed, "t"), c.exp_t)

    if c.exp_dt is not None:
        _assert_eq(errs, "dt", _getattr(parsed, "dt"), c.exp_dt)

    # TZ expectation (only meaningful if dt exists)
    if c.exp_tz_key is not None:
        got_dt = _getattr(parsed, "dt")
        _assert_eq(errs, "dt.tz", _tz_key(got_dt), c.exp_tz_key)

    # leftovers content
    leftovers = _getattr(parsed, "leftovers", "")
    for token in c.leftovers_must_not_contain:
        _assert_not_contains(errs, "leftovers", leftovers, token)

    # price checks (soft / optional)
    if c.price_should_exist is not None:
        price = _getattr(parsed, "price")
        if c.price_should_exist and price is None:
            _fail(errs, "price: expected non-None, got None")
        if (not c.price_should_exist) and price is not None:
            _fail(errs, f"price: expected None, got {price!r}")

        if c.exp_price_amount is not None:
            _assert_eq(errs, "price.amount", _price_amount(price), c.exp_price_amount)
        if c.exp_price_currency is not None:
            _assert_eq(errs, "price.currency", _price_currency(price), c.exp_price_currency)

    return errs


def run_tests() -> None:
    tz = USER_TIMEZONE

    cases: list[Case] = [
        Case(
            name="relative_tomorrow_time",
            raw="Спортзал завтра 03:00",
            now=datetime(2025, 12, 12, 10, 0, tzinfo=tz),
            exp_title="Спортзал",
            exp_d=date(2025, 12, 13),
            exp_t=time(3, 0),
            exp_dt=datetime(2025, 12, 13, 3, 0, tzinfo=tz),
            leftovers_must_not_contain=("завтра", "03:00"),
        ),
        Case(
            name="explicit_ddmm_time",
            raw="созвон 13.12 09:00",
            now=datetime(2025, 12, 12, 10, 0, tzinfo=tz),
            exp_title="созвон",
            exp_d=date(2025, 12, 13),
            exp_t=time(9, 0),
            exp_dt=datetime(2025, 12, 13, 9, 0, tzinfo=tz),
            leftovers_must_not_contain=("13.12", "09:00"),
        ),
        Case(
            name="weekday_next_monday",
            raw="Врач в понедельник 18:30",
            now=datetime(2025, 12, 10, 12, 0, tzinfo=tz),  # Wed
            exp_title="Врач",
            exp_d=date(2025, 12, 15),
            exp_t=time(18, 30),
            exp_dt=datetime(2025, 12, 15, 18, 30, tzinfo=tz),
            leftovers_must_not_contain=("понедельник", "18:30"),
        ),
        Case(
            name="only_time_today",
            raw="Кофе 15:45",
            now=datetime(2025, 12, 12, 9, 0, tzinfo=tz),
            exp_title="Кофе",
            exp_d=date(2025, 12, 12),
            exp_t=time(15, 45),
            exp_dt=datetime(2025, 12, 12, 15, 45, tzinfo=tz),
            leftovers_must_not_contain=("15:45",),
        ),
        Case(
            name="money_and_datetime_soft",
            raw="Кино 1200р завтра 20:00",
            now=datetime(2025, 12, 12, 10, 0, tzinfo=tz),
            exp_title="Кино",
            exp_d=date(2025, 12, 13),
            exp_t=time(20, 0),
            exp_dt=datetime(2025, 12, 13, 20, 0, tzinfo=tz),
            leftovers_must_not_contain=("1200", "1200р", "завтра", "20:00"),
            price_should_exist=True,
            exp_price_amount=1200,
            exp_price_currency="RUB",
        ),
        Case(
            name="no_datetime",
            raw="Купить хлеб и молоко",
            now=datetime(2025, 12, 12, 10, 0, tzinfo=tz),
            exp_title="Купить хлеб и молоко",
            exp_dt=None,
            exp_tz_key=None,  # tz check irrelevant when dt is None
            price_should_exist=False,
        ),
    ]

    total = len(cases)
    failed = 0

    print("=== autocalendar: parse_event_title tests ===")
    for c in cases:
        errs = run_case(c)
        if errs:
            failed += 1
            print(f"\n[FAIL] {c.name}")
            print(f"  raw: {c.raw!r}")
            print(f"  now: {c.now.isoformat()}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"[ OK ] {c.name}")

    print("\n=== summary ===")
    print(f"Total: {total}, Passed: {total - failed}, Failed: {failed}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run_tests()

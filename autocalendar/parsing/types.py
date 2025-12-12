from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class MoneyValue:
    amount: Decimal
    currency: str  # "EUR", "USD", "RUB"


@dataclass(frozen=True)
class ParsedEvent:
    raw: str
    title: str                 # “очищенный” заголовок
    dt: Optional[datetime]     # tz-aware datetime
    d: Optional[date]
    t: Optional[time]
    price: Optional[MoneyValue]
    leftovers: str             # остаток после вырезания сущностей (если хочешь)

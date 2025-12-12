from __future__ import annotations

from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime, date, time
from typing import Optional


@dataclass(frozen=True)
class MoneyValue:
    amount: Decimal
    currency: str  # "EUR", "USD", "RUB"


@dataclass
class ParsedEvent:
    raw: str
    title: str
    dt: Optional[datetime]
    d: Optional[date]
    t: Optional[time]
    price: Optional["MoneyValue"]
    duration: Optional[int]
    explicit_duration: bool
    leftovers: str

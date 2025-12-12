from __future__ import annotations

import re
from decimal import Decimal
from typing import Optional, Tuple

from .types import MoneyValue

_MONEY_RE = re.compile(
    r"(?P<amount>\d+(?:[.,]\d+)?)\s*(?P<cur>€|\$|₽|р|руб\.?|rur|rub|eur|usd)",
    re.IGNORECASE,
)

def extract_money(text: str) -> Tuple[Optional[MoneyValue], str]:
    """
    Возвращает (money, cleaned_text).
    Сейчас — простой regex (без “10к”, “10 000”, “от 10€”).
    """
    m = _MONEY_RE.search(text)
    if not m:
        return None, text

    amount = Decimal(m.group("amount").replace(",", "."))
    cur_raw = m.group("cur").lower()

    currency = (
        "EUR" if cur_raw in {"€", "eur"} else
        "USD" if cur_raw in {"$", "usd"} else
        "RUB"
    )

    cleaned = (text[:m.start()] + text[m.end():]).strip()
    return MoneyValue(amount=amount, currency=currency), cleaned

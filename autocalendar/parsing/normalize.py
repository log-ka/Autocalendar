from __future__ import annotations

import re

_SPACE_RE = re.compile(r"\s+")
_DASH_RE = re.compile(r"[–—]")

def normalize_text(text: str) -> str:
    """
    Нормализация “до парсинга”:
    - выравниваем пробелы
    - приводим тире к дефису
    - убираем мусор по краям
    """
    s = text.strip()
    s = _DASH_RE.sub("-", s)
    s = _SPACE_RE.sub(" ", s)
    return s

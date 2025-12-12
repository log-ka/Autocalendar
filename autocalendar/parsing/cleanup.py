from __future__ import annotations

import re

_SPACE_RE = re.compile(r"\s+")

# Минимальный список “служебных” слов для первого приближения.
# Позже можно расширить и сделать аккуратнее (например, токенизация).
_RELATIVE_WORDS_RE = re.compile(r"\b(сегодня|завтра|послезавтра)\b", re.IGNORECASE)

def cleanup_title(text: str) -> str:
    """
    Финальная чистка заголовка: убираем двойные пробелы и некоторые служебные слова.
    """
    s = _RELATIVE_WORDS_RE.sub("", text)
    s = _SPACE_RE.sub(" ", s).strip(" -")
    return s.strip()

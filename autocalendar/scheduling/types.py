from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True)
class Event:
    """
    Входное событие.

    time = None  → событие гибкое, требует автопланирования
    time != None → событие жёсткое, фиксировано пользователем
    """
    title: str
    date: date
    time: time | None
    duration: int          # длительность в минутах
    priority: int          # чем больше — тем важнее


@dataclass(frozen=True)
class ScheduledEvent:
    """
    Результат автопланирования.
    В отличие от Event, time всегда задан.
    """
    title: str
    date: date
    time: time
    duration: int
    priority: int


@dataclass
class TimeSlot:
    """
    Свободный временной интервал внутри рабочего дня.
    """
    start: time
    end: time

    def duration_minutes(self) -> int:
        """
        Длительность слота в минутах.
        """
        return (
            (self.end.hour * 60 + self.end.minute)
            - (self.start.hour * 60 + self.start.minute)
        )

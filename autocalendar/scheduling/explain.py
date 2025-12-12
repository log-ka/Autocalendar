from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True)
class PlacementReason:
    title: str
    date: date
    time: time
    reason: str


def explain_fixed(title: str, date: date, time: time) -> PlacementReason:
    return PlacementReason(
        title=title,
        date=date,
        time=time,
        reason="Время задано пользователем"
    )


def explain_scheduled(
    title: str,
    date: date,
    time: time,
    slot_start: time
) -> PlacementReason:
    return PlacementReason(
        title=title,
        date=date,
        time=time,
        reason=f"Назначено автоматически в первый доступный слот с {slot_start}"
    )


def explain_overflow(title: str, date: date) -> PlacementReason:
    return PlacementReason(
        title=title,
        date=date,
        time=time(0, 0),
        reason="Перенесено на следующий день из-за нехватки времени"
    )

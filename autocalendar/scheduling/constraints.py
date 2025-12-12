from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class WorkDay:
    start: time
    end: time

    def is_valid(self) -> bool:
        return (self.start.hour, self.start.minute) < (self.end.hour, self.end.minute)

    def duration_minutes(self) -> int:
        return (
            (self.end.hour * 60 + self.end.minute)
            - (self.start.hour * 60 + self.start.minute)
        )

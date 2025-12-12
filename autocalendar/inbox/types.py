from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class InboxItem:
    title: str
    created_at: datetime

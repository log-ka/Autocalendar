from datetime import datetime
from typing import List

from .types import InboxItem


class Inbox:
    def __init__(self):
        self._items: List[InboxItem] = []

    def add(self, title: str):
        self._items.append(
            InboxItem(
                title=title,
                created_at=datetime.now()
            )
        )

    def list(self) -> List[InboxItem]:
        return list(self._items)

    def is_empty(self) -> bool:
        return len(self._items) == 0

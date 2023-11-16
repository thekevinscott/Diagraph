
from typing import Generic, Iterator, TypeVar

T = TypeVar('T')

class OrderedSet(Generic[T]):
    items: list[T]
    _set: set[T]

    def __init__(self, items: set[T] | None):
        self.items = list(items or {})
        self._set = set()

    def add(self, item: T):
        if item not in self._set:
            self._set.add(item)
            self.items.append(item)

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def pop(self) -> T:
        return self.items.pop()

    def __eq__(self, other):
        for item in other:
            if item not in self._set:
                return False
        return True
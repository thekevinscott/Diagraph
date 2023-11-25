from __future__ import annotations

from typing import Generic, TypeVar

Key = TypeVar("Key")
Value = TypeVar("Value")


def is_not_hashable(value):
    if isinstance(value, (list | dict | set)):
        return True

    if isinstance(value, tuple):
        for val in value:
            if is_not_hashable(val):
                return True
    return False


class HistoricalBidict(Generic[Key, Value]):
    keys: dict[Key, list[Value]]
    values_to_keys: dict[Value, Key]

    def __init__(self) -> None:
        self.keys = {}
        self.values_to_keys = {}

    def __str__(self) -> str:
        return str(self.keys)

    def __setitem__(self, key: Key, value: Value) -> None:
        self.keys[key] = [*self.keys.get(key, []), value]
        if is_not_hashable(value) is False:
            self.values_to_keys[value] = key

    def __getitem__(self, key: Key) -> Value:
        if key not in self.keys:
            raise Exception(f"Key {key} not found in {self.keys}")
        if len(self.keys[key]) == 0:
            raise Exception(f"No records found for key {key} not found in {self.keys}")

        return self.keys[key][-1]

    def inverse(self, value: Value) -> Key:
        if is_not_hashable(value):
            raise Exception(
                f"Value {value} is not hashable and cannot be used as an inverse key",
            )
        return self.values_to_keys[value]

    def historical(self, key: Key, index: int) -> Value:
        return self.keys[key][index]

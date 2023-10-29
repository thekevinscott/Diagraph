from typing import Generic, TypeVar

Key = TypeVar("Key")
Value = TypeVar("Value")


class HistoricalBidict(Generic[Key, Value]):
    keys: dict[Key, list[Value]]
    values_to_keys: dict[Value, Key]

    def __init__(self):
        self.keys = {}
        self.values_to_keys = {}

    def __setitem__(self, key: Key, value: Value):
        self.keys[key] = self.keys.get(key, []) + [value]
        self.values_to_keys[value] = key

    def __getitem__(self, key: Key):
        return self.keys[key][-1]

    def inverse(self, value: Value):
        return self.values_to_keys[value]

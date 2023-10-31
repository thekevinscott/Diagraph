import json
from typing import Generic, TypeVar

Key = TypeVar("Key")
Value = TypeVar("Value")


def is_not_hashable(value):
    return isinstance(value, (list, dict, set))


class HistoricalBidict(Generic[Key, Value]):
    keys: dict[Key, list[Value]]
    values_to_keys: dict[Value, Key]

    def __init__(self):
        self.keys = {}
        self.values_to_keys = {}

    def __setitem__(self, key: Key, value: Value):
        self.keys[key] = self.keys.get(key, []) + [value]
        if is_not_hashable(value):
            self.values_to_keys[str(value)] = key
        else:
            self.values_to_keys[value] = key

    def __getitem__(self, key: Key):
        try:
            return self.keys[key][-1]
        except:
            raise Exception(
                f"Could not find key {key} in self keys {json.dumps(self.keys)}"
            )

    def inverse(self, value: Value):
        if is_not_hashable(value):
            return self.values_to_keys[str(value)]
        return self.values_to_keys[value]

    def historical(self, key: Key, index: int):
        return self.keys[key][index]

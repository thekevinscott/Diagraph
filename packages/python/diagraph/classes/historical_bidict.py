import json
from typing import Generic, TypeVar

Key = TypeVar("Key")
Value = TypeVar("Value")


def is_not_hashable(value):
    if isinstance(value, (list, dict, set)):
        return True

    if isinstance(value, tuple):
        for val in value:
            if is_not_hashable(val):
                return True
    return False


class HistoricalBidict(Generic[Key, Value]):
    keys: dict[Key, list[Value]]
    values_to_keys: dict[Value, Key]

    def __init__(self):
        self.keys = {}
        self.values_to_keys = {}

    def __str__(self):
        return str(self.keys)

    def __setitem__(self, key: Key, value: Value):
        self.keys[key] = self.keys.get(key, []) + [value]
        if is_not_hashable(value) is False:
            #     self.values_to_keys[str(value)] = key
            # else:
            self.values_to_keys[value] = key

    def __getitem__(self, key: Key):
        try:
            return self.keys[key][-1]
        except Exception:
            raise Exception(
                f"Could not find key {key} in self keys {json.dumps(self.keys)}"
            )

    def inverse(self, value: Value):
        if is_not_hashable(value):
            raise Exception(
                f"Value {value} is not hashable and cannot be used as an inverse key"
            )
            # return self.values_to_keys[str(value)]
        return self.values_to_keys[value]

    def historical(self, key: Key, index: int):
        return self.keys[key][index]

# This is a class for maintaining state of a diagraph.
# Eventually it will track snapshots of state, but for now, it
# simply records the most recent value
from typing import Any

StateArgs = tuple[Any, ...]
StateKey = tuple[str, ...]
StateValue = Any


class DiagraphStateValue:
    value: StateValue

    def __init__(self, value: StateValue):
        self.value = value


class DiagraphStateValueEmpty:
    ...


class DiagraphStateRecords:
    key: StateKey
    values: dict[int, DiagraphStateValue | DiagraphStateValueEmpty | None]
    snapshot_keys: list[int]

    def __init__(self, key: StateKey):
        self.key = key
        self.values = {}
        self.snapshot_keys = []

    def add(self, snapshot_key: int, value: StateValue):
        self.values[snapshot_key] = DiagraphStateValue(value)
        self.snapshot_keys.append(snapshot_key)

    def get(self, snapshot_key: int):
        value_for_snapshot_key = self.values.get(snapshot_key)
        if value_for_snapshot_key is not None:
            return value_for_snapshot_key.value

        # else, return the most recent value
        most_recent_snapshot_key = self.snapshot_keys[-1]
        value_for_snapshot_key = self.values.get(most_recent_snapshot_key)
        if value_for_snapshot_key is not None:
            return value_for_snapshot_key.value

        raise Exception(f"No value for {self.key} at snapshot key {snapshot_key} found")


class DiagraphState:
    __internal_state__: dict[StateKey, DiagraphStateRecords]
    snapshots: list[int]

    def __init__(self) -> None:
        self.__internal_state__ = {}
        self.snaphots = [0]

    def __get_state__(
        self,
        key: StateKey,
    ) -> StateValue:
        record = self.__internal_state__.get(key)
        if record is None:
            raise Exception(f"No value for {key} found")
        return record.get(self.current_snapshot)

    def __set_state__(
        self,
        key: StateKey,
        value: StateValue,
    ) -> None:
        record = self.__internal_state__.get(key)
        if record is None:
            record = DiagraphStateRecords(key)
            self.__internal_state__[key] = record
        record.add(self.current_snapshot, value)

    def add_snapshot(self):
        self.snaphots.append(len(self.snaphots))

    @property
    def current_snapshot(self):
        return self.snaphots[-1]

    # # def snapshot(snapshot_key: str):
    # #     pass


# We have an array of snapshots
# When getting a value, we'd want to get the value corresponding to that snapshot, _or_ the most recent snapshot

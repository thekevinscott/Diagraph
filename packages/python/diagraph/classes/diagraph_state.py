# This is a class for maintaining state of a diagraph.
# Eventually it will track snapshots of state, but for now, it
# simply records the most recent value
from typing import Any

StateArgs = tuple[Any, ...]
StateKey = tuple[str, ...]
StateValue = Any


class DiagraphState:
    __internal_state__: dict[StateKey, StateValue]

    def __init__(self) -> None:
        self.__internal_state__ = {}

    def __get_state__(
        self,
        key: StateKey,
    ) -> StateValue:
        return self.__internal_state__[key]

    def __set_state__(
        self,
        key: StateKey,
        value: StateValue,
    ) -> None:
        self.__internal_state__[key] = value

    # # def snapshot(snapshot_key: str):
    # #     pass

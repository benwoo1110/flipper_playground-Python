from enum import IntEnum

from ..protocol.protocols import DataHandler, ProtoID, ProtoInterface


class InputKey(IntEnum):
    Up = 0
    Down = 1
    Right = 2
    Left = 3
    Ok = 4
    Back = 5
    MAX = 6


class InputType(IntEnum):
    Press = 0
    Release = 1
    Short = 2
    Long = 3
    Repeat = 4
    MAX = 5


class InputData(DataHandler):
    def __init__(self, key: int, key_type: int):
        self.key: InputKey = InputKey(key)
        self.key_type: InputType = InputType(key_type)

    def __str__(self):
        return f"InputData(key={self.key}, key_type={self.key_type})"

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(data[0], data[1])


class FlipperInput(ProtoInterface):
    def __init__(self) -> None:
        self.add_data_handler(ProtoID.INPUT_ID, InputData)
        super().__init__()

    def input_event(self):
        def decorator(func):
            self.add_event_handler(ProtoID.INPUT_ID, func)
            return func
        return decorator

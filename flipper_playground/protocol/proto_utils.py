import struct

from .protocols import ProtoID


def proto_id_e(proto_id: ProtoID) -> bytes:
    return int16_e(proto_id.value)


def data_size_e(data: bytes) -> bytes:
    return int32_e(len(data))


def int8_e(data: int) -> bytes:
    if data < 0 or data > 255:
        raise ValueError("int8_to_bytes: data must be 0 <= data <= 255")
    return data.to_bytes(1, "little")


def int16_e(data: int) -> bytes:
    if data < 0 or data > 65535:
        raise ValueError("int16_to_bytes: data must be 0 <= data <= 65535")
    return data.to_bytes(2, "little")


def int32_e(data: int) -> bytes:
    if data < 0 or data > 4294967295:
        raise ValueError("int32_to_bytes: data must be 0 <= data <= 4294967295")
    return data.to_bytes(4, "little")


def float32_e(data: float) -> bytes:
    return struct.pack("f", data)


def str_e(data: str) -> bytes:
    return int32_e(len(data)) + data.encode("utf-8")


def payload_e(id: ProtoID, data: bytes) -> bytes:
    return proto_id_e(id) + data_size_e(data) + data

from enum import IntEnum
import os
import sys
from typing import Union
from typing_extensions import Literal, SupportsIndex

import serial.tools.list_ports

class ProtoID(IntEnum):
    CNT_FLIPPER_START_ID = 0x0001
    CNT_PYTHON_START_ID = 0x0002
    CNT_FLIPPER_STOP_ID = 0xFFF1
    CNT_PYTHON_STOP_ID = 0xFFF2

    INPUT_ID = 0x1001

    GUI_DRAW_ID = 0x2000
    GUI_DRAW_STR_ID = 0x2001
    GUI_DRAW_STR_ALIGN_ID = 0x2002
    GUI_DRAW_FRAME_ID = 0x2003
    GUI_DRAW_RFRAME_ID = 0x2004

class Align(IntEnum):
    Left = 0
    Right = 1
    Top = 2
    Bottom = 3
    Center = 4

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

class InputData:
    def __init__(self, key: int, key_type: int):
        self.key = InputKey(key)
        self.key_type = InputType(key_type)
    
    def __str__(self):
        return f"InputData(key={self.key}, key_type={self.key_type})"

class Canvas:
    def __init__(self) -> None:
        self.draw_count = 0
        self.draw_data = b''

    def compile_draw_data(self):
        return int16_e(self.draw_count) + self.draw_data

    def draw_str(self, x: int, y: int, msg: str):
        draw_str_data = int8_e(x) + int8_e(y) + str_e(msg)
        self._add_draw(ProtoID.GUI_DRAW_STR_ID, draw_str_data)

    def draw_str_align(self, x:int, y: int, horizontal: Align, vertical: Align, msg: str):
        draw_str_align_data = int8_e(x) + int8_e(y) + int8_e(horizontal) + int8_e(vertical) + str_e(msg)
        self._add_draw(ProtoID.GUI_DRAW_STR_ALIGN_ID, draw_str_align_data)

    def draw_frame(self, x, y, width, height):
        draw_frame_data = int8_e(x) + int8_e(y) + int8_e(width) + int8_e(height)
        self._add_draw(ProtoID.GUI_DRAW_FRAME_ID, draw_frame_data)

    def draw_rframe(self, x, y, width, height, radius):
        draw_rframe_data = int8_e(x) + int8_e(y) + int8_e(width) + int8_e(height) + int8_e(radius)
        self._add_draw(ProtoID.GUI_DRAW_RFRAME_ID, draw_rframe_data)
    
    def _add_draw(self, proto_id: ProtoID, data: bytes):
        self.draw_data += payload_e(proto_id, data)
        self.draw_count += 1

class Flipper:
    def __init__(self):
        self.serial = None
        self.input_callback_func = None
        self.running = False

    def open_serial(self, port=None, timeout=None) -> serial.Serial:
        serial_port = port or self._find_port()

        if serial_port is None:
            print("can not find Flipper serial dev")
            sys.exit(0)

        if not os.path.exists(serial_port):
            print(f"can not open {serial_port}")
            sys.exit(0)

        # open serial port
        self.serial = serial.Serial(serial_port, timeout=1)
        self.serial.baudrate = 230400
        self.serial.flushOutput()
        self.serial.flushInput()

        self.serial.timeout = timeout

    def _find_port(self) -> Union[str, None]:
        # COM4: USB Serial Device (COM4) [USB VID:PID=0483:5740 SER=FLIP_UNYANA LOCATION=1-3:x.0]
        # /dev/cu.usbmodemflip_Unyana1: Flipper Unyana [USB VID:PID=0483:5740 SER=flip_Unyana LOCATION=20-2]
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in ports:
            a = hwid.split()
            if "VID:PID=0483:5740" in a:
                return port

        return None
    
    def receive(self):
        id_raw = self.serial.read(2)
        id = int.from_bytes(id_raw, "little")
        data_size_raw = self.serial.read(4)
        data_size = int.from_bytes(data_size_raw, "little")
        if data_size == 0:
            return id, b''
        data = self.serial.read(data_size)
        return id, data

    def send(self, id: ProtoID, data: bytes = b''):
        self.serial.write(payload_e(id, data))

    def close(self):
        self.send(ProtoID.CNT_PYTHON_STOP_ID)

    def draw(self, canvas: Canvas):
        self.send(ProtoID.GUI_DRAW_ID, canvas.compile_draw_data())

    def input_callback(self):
        def decorator(func):
            self.input_callback_func = func
            return func
        return decorator

    def event_loop(self):
        if self.running:
            # error
            return

        # start running
        self.running = True
        
        # ignore the header
        out = self.serial.read_until(b">: ").decode("utf-8")
        
        # run the python playground command
        print("starting...")
        self.serial.write(b"python_playground\r\n")
        self.serial.read_until(b"python_playground\r\n")

        id, data = self.receive()
        if id != ProtoID.CNT_FLIPPER_START_ID:
            print("failed to start")
            sys.exit(0)
        
        print("started!")

        while self.running:
            id, data = self.receive()
            if id == ProtoID.CNT_FLIPPER_STOP_ID:
                break
            elif id == ProtoID.INPUT_ID:
                input_data = InputData(data[0], data[1])
                self.input_callback_func(input_data)
        
        self.serial.close()
        self.running = False
        print("stopped!")

# Utils methods
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

def str_e(data: str) -> bytes:
    return int32_e(len(data)) + data.encode("utf-8")

def payload_e(id: ProtoID, data: bytes) -> bytes:
    return proto_id_e(id) + data_size_e(data) + data

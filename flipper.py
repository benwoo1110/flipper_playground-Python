from enum import IntEnum
import os
import sys
from typing import Union

import serial.tools.list_ports

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

    def draw_str(self, x, y, msg):
        draw_str_data = x.to_bytes(1, "little") + y.to_bytes(1, "little") + msg.encode("utf-8") + b"\0"
        self.draw_data += 0x2001.to_bytes(2, "little") + len(draw_str_data).to_bytes(4, "little") + draw_str_data
        self.draw_count += 1
    
    def draw_frame(self, x, y, width, height):
        draw_frame_data = x.to_bytes(1, "little") + y.to_bytes(1, "little") + width.to_bytes(1, "little") + height.to_bytes(1, "little")
        self.draw_data += 0x2003.to_bytes(2, "little") + len(draw_frame_data).to_bytes(4, "little") + draw_frame_data
        self.draw_count += 1

    def compile_draw_data(self):
        return self.draw_count.to_bytes(2, "little") + self.draw_data

class Flipper:
    def __init__(self):
        self.serial = None
        self.input_callback_func = None

    def open_serial(self, port=None, timeout=None) -> serial.Serial:
        """open serial device"""
        
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

    # COM4: USB Serial Device (COM4) [USB VID:PID=0483:5740 SER=FLIP_UNYANA LOCATION=1-3:x.0]
    # /dev/cu.usbmodemflip_Unyana1: Flipper Unyana [USB VID:PID=0483:5740 SER=flip_Unyana LOCATION=20-2]
    def _find_port(self) -> Union[str, None]:
        """find serial device"""

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

    def send(self, id: int, data: bytes):
        print(id, data)
        self.serial.write(id.to_bytes(2, "little") + len(data).to_bytes(4, "little") + data)

    def draw(self, canvas: Canvas):
        self.send(0x2000, canvas.compile_draw_data())

    def input_callback(self):
        def decorator(func):
            self.input_callback_func = func
            return func
        return decorator

    def event_loop(self):
        # ignore the header
        out = self.serial.read_until(b">: ").decode("utf-8")

        self.serial.write(b"python_playground\r\n")
        print("starting...")

        self.serial.readline()
        start_msg = self.serial.readline().decode("utf-8").strip()
        if start_msg != "CLI Connection Start":
            print("failed to start")
            sys.exit(0)
        
        print("started!")

        while True:
            id, data = self.receive()
            if id == 0x0001:
                break
            elif id == 0x1001:
                input_data = InputData(data[0], data[1])
                self.input_callback_func(input_data)

import os
import sys
import time
from enum import IntEnum
from typing import Union

from serial import Serial
from serial.tools import list_ports

from protocol import ProtoID, float32_e, int8_e, int16_e, payload_e, str_e


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
        self.key: InputKey = InputKey(key)
        self.key_type: InputType = InputType(key_type)

    def __str__(self):
        return f"InputData(key={self.key}, key_type={self.key_type})"


class Canvas:
    def __init__(self) -> None:
        self.draw_count = 0
        self.draw_data = bytearray()

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
        self.draw_data.extend(payload_e(proto_id, data))
        self.draw_count += 1


class Flipper:
    def __init__(self):
        self.serial: Serial = None
        self.running: bool = False
        self.input_callback_func: callable = None
        self.draw_callback_func: callable = None
        self.connected_callback_func: callable = None
        self.disconnected_callback_func: callable = None

    def open_serial(self, port=None, timeout=1):
        serial_port = port or self._find_port()

        if serial_port is None:
            print("can not find Flipper serial dev")
            sys.exit(0)

        if not os.path.exists(serial_port):
            print(f"can not open {serial_port}")
            sys.exit(0)

        # open serial port
        self.serial = Serial(serial_port, timeout=1)
        self.serial.baudrate = 230400
        self.serial.flushOutput()
        self.serial.flushInput()

        self.serial.timeout = timeout

    def _find_port(self) -> Union[str, None]:
        # COM4: USB Serial Device (COM4) [USB VID:PID=0483:5740 SER=FLIP_UNYANA LOCATION=1-3:x.0]
        # /dev/cu.usbmodemflip_Unyana1: Flipper Unyana [USB VID:PID=0483:5740 SER=flip_Unyana LOCATION=20-2]
        ports = list_ports.comports()
        for port, desc, hwid in ports:
            a = hwid.split()
            if "VID:PID=0483:5740" in a:
                return port

        return None

    def receive(self) -> (ProtoID, bytes):
        id_raw = self.serial.read(2)
        if len(id_raw) != 2:
            return None, None
        
        id = int.from_bytes(id_raw, "little")

        data_size_raw = self.serial.read(4)
        if len(data_size_raw) != 4:
            return None, None
        
        data_size = int.from_bytes(data_size_raw, "little")
        if data_size == 0:
            return id, None

        data = self.serial.read(data_size)
        if len(data) != data_size:
            return None, None

        return id, data

    def send(self, id: ProtoID, data: bytes = b''):
        self.serial.write(payload_e(id, data))

    def send_close(self):
        self.send(ProtoID.CNT_PYTHON_STOP_ID)

    def send_draw(self, canvas: Canvas):
        self.send(ProtoID.GUI_DRAW_ID, canvas.compile_draw_data())

    def send_speaker_play(self, frequency: float, volume: float):
        self.send(ProtoID.SPEAKER_PLAY_ID, float32_e(frequency) + float32_e(volume))

    def send_speaker_stop(self):
        self.send(ProtoID.SPEAKER_STOP_ID)

    def input_callback(self):
        def decorator(func):
            self.input_callback_func = func
            return func
        return decorator

    def connected_callback(self):
        def decorator(func):
            self.connected_callback_func = func
            return func
        return decorator
    
    def disconnected_callback(self):
        def decorator(func):
            self.disconnected_callback_func = func
            return func
        return decorator

    def draw_callback(self):
        def decorator(func):
            self.draw_callback_func = func
            return func
        return decorator

    def set_input_callback(self, func):
        self.input_callback_func = func

    def set_draw_callback(self, func):
        self.draw_callback_func = func

    def update_view(self):
        canvas = Canvas()
        if self.draw_callback_func:
            self.draw_callback_func(canvas)
        self.send_draw(canvas)

    def event_loop(self):
        if self.running:
            # error
            return

        # start running
        self.running = True

        try:
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

            # Wait for flipper to enter the main loop
            time.sleep(0.1)
            if self.connected_callback_func:
                self.connected_callback_func()
            
            print("started!")

            while self.running:
                id, data = self.receive()
                if id == ProtoID.CNT_FLIPPER_STOP_ID:
                    break
                elif id == ProtoID.INPUT_ID:
                    input_data = InputData(data[0], data[1])
                    if self.input_callback_func:
                        self.input_callback_func(input_data)

        except KeyboardInterrupt:
            pass

        finally:
            print("stopping...")
            if self.disconnected_callback_func:
                self.disconnected_callback_func()
            self.serial.close()
            self.running = False
            print("stopped!")

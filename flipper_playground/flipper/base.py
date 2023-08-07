import os
import sys
import time
from typing import Union

from serial import Serial
from serial.tools import list_ports

from .draw import FlipperDraw
from .input import FlipperInput
from .hardware import FlipperHardware
from ..protocol.protocols import ProtoID, ProtoParser, ProtoEventManager
from ..protocol.proto_utils import payload_e


class Flipper(
    ProtoParser,
    ProtoEventManager,
    FlipperDraw,
    FlipperInput,
    FlipperHardware,
):
    def __init__(self):
        self.serial: Serial = None
        self.running: bool = False
        super().__init__()

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

        return id, self.parse_bytes(id, data)

    def send(self, id: ProtoID, data: bytes = b''):
        self.serial.write(payload_e(id, data))

    def send_close(self):
        self.send(ProtoID.CNT_PYTHON_STOP_ID)

    def start_event(self):
        def decorator(func):
            self.add_event_handler(ProtoID.CNT_FLIPPER_START_ID, func)
            return func
        return decorator
    
    def stop_event(self):
        def decorator(func):
            self.add_event_handler(ProtoID.CNT_FLIPPER_STOP_ID, func)
            return func
        return decorator

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
            self.handle_event(id, data)

            print("started!")

            while self.running:
                id, data = self.receive()
                if id is None:
                    continue
                self.handle_event(id, data)
                if id == ProtoID.CNT_FLIPPER_STOP_ID:
                    break

        except KeyboardInterrupt:
            pass

        finally:
            print("stopping...")
            self.serial.close()
            self.running = False
            print("stopped!")

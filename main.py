import sys
import os
from typing import Union
from random import randint

import serial
import serial.tools.list_ports

# COM4: USB Serial Device (COM4) [USB VID:PID=0483:5740 SER=FLIP_UNYANA LOCATION=1-3:x.0]
# /dev/cu.usbmodemflip_Unyana1: Flipper Unyana [USB VID:PID=0483:5740 SER=flip_Unyana LOCATION=20-2]
def find_port() -> Union[str, None]:  # -> str | None:
    """find serial device"""

    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in ports:
        a = hwid.split()
        if "VID:PID=0483:5740" in a:
            return port

    return None

def open_serial(custom_port=None) -> serial.Serial:
    """open serial device"""

    serial_port = custom_port or find_port()

    if serial_port is None:
        print("can not find Flipper serial dev")
        sys.exit(0)

    if not os.path.exists(serial_port):
        print(f"can not open {serial_port}")
        sys.exit(0)

    # open serial port
    flipper = serial.Serial(serial_port, timeout=1)
    flipper.baudrate = 230400
    flipper.flushOutput()
    flipper.flushInput()

    # disable timeout
    flipper.timeout = None

    return flipper

if __name__ == "__main__":
    flipper = open_serial()
    print(flipper)

    # ignore the header
    out = flipper.read_until(b">: ").decode("utf-8")

    flipper.write(b"python_playground\r\n")
    print("starting...")

    flipper.readline()
    start_msg = flipper.readline().decode("utf-8").strip()
    if start_msg != "CLI Connection Start":
        print("failed to start")
        sys.exit(0)
    
    print("started!")

    while True:
        id_raw = flipper.read(2)
        id = int.from_bytes(id_raw, "little")
        print("id:", id)
        if id == 0x1001:
            data_size_raw = flipper.read(4)
            data_size = int.from_bytes(data_size_raw, "little")
            print("data_size:", data_size)
            data = flipper.read(data_size)
            key = data[0]
            keytype = data[1]
            print("key:", key)
            print("keytype:", keytype)

            if data == b"CLOSE":
                print("closing!")
                break

            send_size = 5
            send_size_bytes = send_size.to_bytes(4, "little")
            x = randint(32, 96).to_bytes(1, "little")
            y = randint(16, 48).to_bytes(1, "little")
            flipper.write(b"\x01\x20" + send_size_bytes + x + y + b"OK\x00")

    flipper.close()
    print("closed!")

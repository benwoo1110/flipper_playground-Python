from enum import IntEnum

from ..protocol.protocols import ProtoInterface
from ..protocol.proto_utils import ProtoID, int8_e, float32_e, str_e


class Light(IntEnum):
    Red = 1 << 0
    Green = 1 << 1
    Blue = 1 << 2
    Backlight = 1 << 3


class FlipperHardware(ProtoInterface):
    def __init__(self) -> None:
        super().__init__()

    def send_speaker_play(self, frequency: float, volume: float):
        self.send(ProtoID.HW_SPEAKER_PLAY_ID, float32_e(frequency) + float32_e(volume))

    def send_speaker_stop(self):
        self.send(ProtoID.HW_SPEAKER_STOP_ID)

    def send_speaker_change_volume(self, volume: float):
        self.send(ProtoID.HW_SPEAKER_CHANGE_VOLUME_ID, float32_e(volume))
    
    def send_vibrator_on(self):
        self.send(ProtoID.HW_VIBRATOR_ON_ID)
    
    def send_vibrator_off(self):
        self.send(ProtoID.HW_VIBRATOR_OFF_ID)

    def send_light_set(self, light: Light, value: int):
        self.send(ProtoID.HW_LIGHT_SET_ID, int8_e(light) + int8_e(value))
    
    def send_light_sequence(self, sequence: str):
        self.send(ProtoID.HW_LIGHT_SEQUENCE_ID, str_e(sequence))

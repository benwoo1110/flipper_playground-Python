import time
import random

from flipper_playground import Align, Canvas, Flipper, InputData, InputKey, InputType, Light, ProtoID

sound = False
key_name = '?'
key_type_name = '?'


flipper = Flipper()


@flipper.event_handler(ProtoID.CNT_PYTHON_START_ID)
def connected_callback():
    print("connected_callback")
    flipper.update_view()


@flipper.event_handler(ProtoID.CNT_PYTHON_STOP_ID)
def disconnected_callback():
    print("disconnected_callback")


@flipper.input_event()
def input_callback(data: InputData):
    global sound, key_name, key_type_name

    start = time.perf_counter_ns()

    if data.key == InputKey.Ok and data.key_type == InputType.Short:
        if sound:
            flipper.send_speaker_stop()
            flipper.send_vibrator_off()
            flipper.send_light_set(Light.Red | Light.Green | Light.Blue, 0x00)
            sound = False
        else:
            flipper.send_speaker_play(554, 0.3)
            #flipper.send_vibrator_on()
            flipper.send_light_set(Light.Green, random.randint(0, 0xFF))
            flipper.send_light_set(Light.Red, random.randint(0, 0xFF))
            flipper.send_light_set(Light.Blue, random.randint(0, 0xFF))
            sound = True

    key_name = data.key.name
    key_type_name = data.key_type.name
    flipper.update_view()

    print(f"input_callback: {(time.perf_counter_ns() - start) / 1000000} ms")


@flipper.draw_callback()
def draw_callback(canvas: Canvas):
    canvas.draw_str_align(64, 28, Align.Center, Align.Center, key_name)
    canvas.draw_str_align(64, 38, Align.Center, Align.Center, key_type_name)
    canvas.draw_rframe(34, 18, 60, 30, 8)


flipper.open_serial()
flipper.event_loop()

import time

from flipper import Align, Canvas, Flipper, InputData, InputKey, InputType

sound = False
key_name = '?'
key_type_name = '?'


flipper = Flipper()
flipper.open_serial()


@flipper.input_callback()
def input_callback(data: InputData):
    global sound, key_name, key_type_name

    start = time.perf_counter_ns()

    if data.key == InputKey.Ok and data.key_type == InputType.Short:
        if sound:
            flipper.send_speaker_stop()
            sound = False
        else:
            flipper.send_speaker_play(554, 0.3)
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


flipper.event_loop()

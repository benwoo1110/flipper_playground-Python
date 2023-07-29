import time

from flipper import Align, Canvas, Flipper, InputData, InputKey, InputType


box_x = 10
box_y = 10
key_name = '?'
key_type_name = '?'

flipper = Flipper()
flipper.open_serial()


@flipper.input_callback()
def input_callback(data: InputData):
    global box_x, box_y, key_name, key_type_name

    start = time.perf_counter_ns()
    if data.key_type != InputType.Short and data.key_type != InputType.Repeat:
        return
    
    if data.key == InputKey.Up:
        box_y -= 1
    elif data.key == InputKey.Down:
        box_y += 1
    elif data.key == InputKey.Left:
        box_x -= 1
    elif data.key == InputKey.Right:
        box_x += 1

    key_name = data.key.name
    key_type_name = data.key_type.name

    flipper.update_view()
    print(f"input_callback: {(time.perf_counter_ns() - start) / 1000000} ms")


@flipper.draw_callback()
def draw_callback(canvas: Canvas):
    canvas.draw_str_align(120, 10, Align.Right, Align.Center, key_name)
    canvas.draw_str_align(120, 20, Align.Right, Align.Center, key_type_name)
    for i in range(4, 30):
        canvas.draw_rframe(box_x, box_y, i, i, 2)


flipper.event_loop()

from random import randint

from flipper import Align, Canvas, Flipper, InputData, InputKey, InputType

box_x = 10
box_y = 10

flipper = Flipper()
flipper.open_serial()

@flipper.input_callback()
def input_callback(data: InputData):
    global box_x, box_y

    #print(data)
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

    canvas = Canvas()
    canvas.draw_str_align(120, 10, Align.Right, Align.Center, data.key.name)
    canvas.draw_str_align(120, 20, Align.Right, Align.Center, data.key_type.name)
    for i in range(8, 31, 2):
        canvas.draw_rframe(box_x, box_y, i, i, 2)
    # print(canvas.draw_count)
    # print(canvas.draw_data)
    flipper.draw(canvas)

flipper.event_loop()

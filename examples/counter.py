from flipper_playground import Flipper, Canvas, Align, InputData, InputKey, InputType, Font


class Counter:
    def __init__(self) -> None:
        self.count = 0

    def increment(self):
        self.count += 1

    def decrement(self):
        self.count -= 1

    def reset(self):
        self.count = 0


flipper = Flipper()
counter = Counter()


@flipper.start_event()
def connected_callback():
    print("connected_callback")
    flipper.update_view()


@flipper.stop_event()
def disconnected_callback():
    print("disconnected_callback")


@flipper.input_event()
def input_callback(data: InputData):
    print(data)
    if data.key in (InputKey.Right, InputKey.Up) and data.key_type in (InputType.Short, InputType.Repeat):
        counter.increment()
    elif data.key == (InputKey.Left, InputKey.Down) and data.key_type in (InputType.Short, InputType.Repeat):
        counter.decrement()
    elif data.key == InputKey.Ok and data.key_type == InputType.Long:
        counter.reset()
    flipper.update_view()


@flipper.draw_callback()
def draw_callback(canvas: Canvas):
    canvas.set_font(Font.Primary)
    canvas.draw_str_align(64, 10, Align.Center, Align.Center, "Bennnn Counter")
    canvas.set_font(Font.BigNumbers)
    canvas.draw_str_align(64, 38, Align.Center, Align.Center, str(counter.count))
    canvas.draw_rframe(44, 22, 40, 32, 8)


flipper.open_serial()
flipper.event_loop()

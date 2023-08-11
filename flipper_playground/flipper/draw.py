from enum import IntEnum

from ..protocol.icon import file2icon
from ..protocol.protocols import ProtoInterface
from ..protocol.proto_utils import ProtoID, bytes_e, int8_e, int16_e, str_e, payload_e


class Align(IntEnum):
    Left = 0
    Right = 1
    Top = 2
    Bottom = 3
    Center = 4


class CanvasDirection(IntEnum):
    LeftToRight = 0
    TopToBottom = 1
    RightToLeft = 2
    BottomToTop = 3


class Color(IntEnum):
    White = 0x00
    Black = 0x01
    XOR = 0x02


class Font(IntEnum):
    Primary = 0
    Secondary = 1
    Keyboard = 2
    BigNumbers = 3
    BatteryPercent = 4
    TotalNumber = 5


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

    def draw_str_align_center(self, x: int, y: int, msg: str):
        self.draw_str_align(x, y, Align.Center, Align.Center, msg)

    def draw_frame(self, x, y, width, height):
        draw_frame_data = int8_e(x) + int8_e(y) + int8_e(width) + int8_e(height)
        self._add_draw(ProtoID.GUI_DRAW_FRAME_ID, draw_frame_data)

    def draw_rframe(self, x, y, width, height, radius):
        draw_rframe_data = int8_e(x) + int8_e(y) + int8_e(width) + int8_e(height) + int8_e(radius)
        self._add_draw(ProtoID.GUI_DRAW_RFRAME_ID, draw_rframe_data)

    def draw_icon(self, x, y, icon_id):
        draw_icon_data = int8_e(x) + int8_e(y) + int8_e(icon_id)
        self._add_draw(ProtoID.GUI_DRAW_ICON_ID, draw_icon_data)

    def draw_dot(self, x, y):
        draw_dot_data = int8_e(x) + int8_e(y)
        self._add_draw(ProtoID.GUI_DRAW_DOT_ID, draw_dot_data)
    
    def draw_line(self, x1, y1, x2, y2):
        draw_line_data = int8_e(x1) + int8_e(y1) + int8_e(x2) + int8_e(y2)
        self._add_draw(ProtoID.GUI_DRAW_LINE_ID, draw_line_data)
    
    def draw_circle(self, x, y, radius):
        draw_circle_data = int8_e(x) + int8_e(y) + int8_e(radius)
        self._add_draw(ProtoID.GUI_DRAW_CIRCLE_ID, draw_circle_data)
    
    def draw_disc(self, x, y, radius):
        draw_disc_data = int8_e(x) + int8_e(y) + int8_e(radius)
        self._add_draw(ProtoID.GUI_DRAW_DISC_ID, draw_disc_data)
    
    def draw_triangle(self, x, y, base, height, direction):
        draw_triangle_data = int8_e(x) + int8_e(y) + int8_e(base) + int8_e(height) + int8_e(direction)
        self._add_draw(ProtoID.GUI_DRAW_TRIANGLE_ID, draw_triangle_data)

    def draw_glyph(self, x, y, glyph_char):
        draw_glyph_data = int8_e(x) + int8_e(y) + int16_e(glyph_char)
        self._add_draw(ProtoID.GUI_DRAW_GLYPH_ID, draw_glyph_data)

    def draw_box(self, x, y, width, height):
        draw_box_data = int8_e(x) + int8_e(y) + int8_e(width) + int8_e(height)
        self._add_draw(ProtoID.GUI_DRAW_BOX_ID, draw_box_data)

    def draw_rbox(self, x, y, width, height, radius):
        draw_rbox_data = int8_e(x) + int8_e(y) + int8_e(width) + int8_e(height) + int8_e(radius)
        self._add_draw(ProtoID.GUI_DRAW_RBOX_ID, draw_rbox_data)

    def set_color(self, color: Color):
        set_color_data = int8_e(color)
        self._add_draw(ProtoID.GUI_SET_COLOR_ID, set_color_data)
    
    def set_color_inverted(self):
        self._add_draw(ProtoID.GUI_SET_COLOR_INVERTED_ID, b'')
    
    def set_font(self, font: Font):
        set_font_data = int8_e(font)
        self._add_draw(ProtoID.GUI_SET_FONT_ID, set_font_data)

    def set_font_direction(self, direction: CanvasDirection):
        set_font_direction_data = int8_e(direction)
        self._add_draw(ProtoID.GUI_SET_FONT_DIRECTION_ID, set_font_direction_data)

    def _add_draw(self, proto_id: ProtoID, data: bytes):
        self.draw_data.extend(payload_e(proto_id, data))
        self.draw_count += 1


class FlipperDraw(ProtoInterface):
    def __init__(self) -> None:
        self._draw_callback: callable = None
        super().__init__()

    def draw_callback(self):
        def decorator(func):
            self._draw_callback = func
            return func
        return decorator
    
    def set_draw_callback(self, func: callable):
        self._draw_callback = func

    def send_draw(self, canvas: Canvas):
        self.send(ProtoID.GUI_DRAW_ID, canvas.compile_draw_data())

    def send_icon_add(self, icon_id: int, file_path: str):
        icon = file2icon(file_path)
        print(icon)
        self.send(ProtoID.GUI_ICON_ADD_ID, int8_e(icon_id) + int8_e(icon.width) + int8_e(icon.height) + bytes_e(icon.data))

    def update_view(self):
        canvas = Canvas()
        if self._draw_callback:
            self._draw_callback(canvas)
        self.send_draw(canvas)

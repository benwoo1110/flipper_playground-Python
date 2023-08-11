from enum import IntEnum


class ProtoID(IntEnum):
    CNT_FLIPPER_START_ID = 0x0001
    CNT_PYTHON_START_ID = 0x0002
    CNT_FLIPPER_STOP_ID = 0xFFF1
    CNT_PYTHON_STOP_ID = 0xFFF2

    INPUT_ID = 0x1001

    GUI_DRAW_ID = 0x2000
    GUI_DRAW_STR_ID = 0x2001
    GUI_DRAW_STR_ALIGN_ID = 0x2002
    GUI_DRAW_FRAME_ID = 0x2003
    GUI_DRAW_RFRAME_ID = 0x2004
    GUI_DRAW_ICON_ID = 0x2005
    GUI_DRAW_DOT_ID = 0x2006
    GUI_DRAW_LINE_ID = 0x2007
    GUI_DRAW_CIRCLE_ID = 0x2008
    GUI_DRAW_DISC_ID = 0x2009
    GUI_DRAW_TRIANGLE_ID = 0x200A
    GUI_DRAW_GLYPH_ID = 0x200B
    GUI_DRAW_BOX_ID = 0x200C
    GUI_DRAW_RBOX_ID = 0x200D

    GUI_DRAW_PROGRESS_BAR_ID = 0x2100
    GUI_DRAW_PROGRESS_BAR_TEXT_ID = 0x2101
    GUI_DRAW_SCROLLBAR_ID = 0x2102
    GUI_DRAW_SCROLLBAR_POS_ID = 0x2103
    GUI_DRAW_BUTTON_LEFT_ID = 0x2104
    GUI_DRAW_BUTTON_RIGHT_ID = 0x2105
    GUI_DRAW_BUTTON_CENTER_ID = 0x2106
    GUI_DRAW_MULTILINE_TEXT_ID = 0x2107
    GUI_DRAW_MULTILINE_TEXT_ALIGN_ID = 0x2108
    GUI_DRAW_MULTILINE_TEXT_FRAMED_ID = 0x2109
    GUI_DRAW_SLIGHTLY_ROUNDED_FRAME_ID = 0x210A
    GUI_DRAW_SLIGHTLY_ROUNDED_BOX_ID = 0x210B
    GUI_DRAW_BOLD_ROUNDED_FRAME_ID = 0x210C
    GUI_DRAW_BUBBLE_ID = 0x210D
    GUI_DRAW_BUBBLE_STR_ID = 0x210E
    GUI_DRAW_STRING_FIT_WIDTH_ID = 0x210F
    GUI_DRAW_SCROLLABLE_TEXT_ID = 0x2110
    GUI_DRAW_SCROLLABLE_TEXT_CENTER_ID = 0x2111

    GUI_ICON_ADD_ID = 0x2200

    HW_SPEAKER_PLAY_ID = 0x3000
    HW_SPEAKER_STOP_ID = 0x3001
    HW_SPEAKER_SET_VOLUME_ID = 0x3002
    HW_VIBRATOR_ON_ID = 0x3003
    HW_VIBRATOR_OFF_ID = 0x3004
    HW_LIGHT_SET_ID = 0x3005
    HW_LIGHT_SEQUENCE_ID = 0x3006


class DataHandler:
    @classmethod
    def from_bytes(cls, data: bytes):
        raise NotImplementedError


class ProtoInterface:
    def send(self, proto_id: ProtoID, data: bytes = b''):
        raise NotImplementedError

    def add_data_handler(self, proto_id: ProtoID, handler: DataHandler):
        raise NotImplementedError
    
    def add_event_handler(self, proto_id: ProtoID, handler: callable):
        raise NotImplementedError


class ProtoParser:
    def __init__(self):
        print("2")
        self.data_handlers: dict[ProtoID, DataHandler] = {}
        super().__init__()
    
    def add_data_handler(self, proto_id: ProtoID, handler: DataHandler):
        self.data_handlers[proto_id] = handler

    def parse_bytes(self, id: ProtoID, data: bytes):
        if id in self.data_handlers:
            return self.data_handlers[id].from_bytes(data)
        else:
            print("Unknown proto id: " + str(id))
            return data


class ProtoEventManager:
    def __init__(self):
        print("1")
        self.event_handlers: dict[ProtoID, list[callable]] = {}
        super().__init__()
    
    def event_handler(self, proto_id: ProtoID):
        def decorator(f):
            self.add_event_handler(proto_id, f)
            return f
        return decorator

    def add_event_handler(self, proto_id: ProtoID, handler: callable):
        if proto_id not in self.event_handlers:
            self.event_handlers[proto_id] = []
        self.event_handlers[proto_id].append(handler)

    def handle_event(self, id: ProtoID, data: object=None):
        print(f"Handling event: {id}")
        if id in self.event_handlers:
            for handler in self.event_handlers[id]:
                if data is None: handler()
                else: handler(data)
        else:
            print("Unknown proto id: " + str(id))

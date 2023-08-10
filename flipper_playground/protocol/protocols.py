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
    GUI_ICON_ADD_ID = 0x2101

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

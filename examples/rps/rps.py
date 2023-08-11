from enum import IntEnum
from random import randint

from flipper_playground import Flipper, Canvas, InputData, InputKey, InputType


class RPSIcons(IntEnum):
    Rock = 0
    Paper = 1
    Scissor = 2
    Empty = 3


class RPS:
    outcomes = {
        (RPSIcons.Rock, RPSIcons.Rock): 0,
        (RPSIcons.Rock, RPSIcons.Paper): -1,
        (RPSIcons.Rock, RPSIcons.Scissor): 1,
        (RPSIcons.Paper, RPSIcons.Rock): 1,
        (RPSIcons.Paper, RPSIcons.Paper): 0,
        (RPSIcons.Paper, RPSIcons.Scissor): -1,
        (RPSIcons.Scissor, RPSIcons.Rock): -1,
        (RPSIcons.Scissor, RPSIcons.Paper): 1,
        (RPSIcons.Scissor, RPSIcons.Scissor): 0,
    }

    def __init__(self) -> None:
        self.player = RPSIcons.Empty
        self.opponent = RPSIcons.Empty
        self.player_score = 0
        self.opponent_score = 0
        self.play_complete = False
        self.message = "<- VS ->"

    def player_next(self):
        self.player = (self.player + 1) % RPSIcons.Empty

    def player_prev(self):
        self.player = (self.player - 1) % RPSIcons.Empty

    def opponent_set(self):
        self.opponent = randint(0, 2)

    def reset(self):
        self.player = RPSIcons.Empty
        self.opponent = RPSIcons.Empty
        self.play_complete = False

    def play(self):
        if self.player == RPSIcons.Empty:
            return

        rps.opponent_set()
        result = self.outcomes[(self.player, self.opponent)]
        if result == 1:
            self.player_score += 1
        elif result == -1:
            self.opponent_score += 1
        self.play_complete = True
        return result


rps = RPS()
flipper = Flipper()


@flipper.start_event()
def start_event():
    print("connected_callback")
    flipper.send_icon_add(RPSIcons.Rock, "assets/rock.png")
    flipper.send_icon_add(RPSIcons.Paper, "assets/paper.png")
    flipper.send_icon_add(RPSIcons.Scissor, "assets/scissor.png")
    flipper.send_icon_add(RPSIcons.Empty, "assets/empty.png")
    flipper.update_view()


@flipper.stop_event()
def stop_event():
    print("disconnected_callback")


@flipper.input_event()
def input_event(event: InputData):
    if event.key == InputKey.Up \
    and event.key_type == InputType.Short \
    and not rps.play_complete:
        rps.player_next()
    
    elif event.key == InputKey.Down \
    and event.key_type == InputType.Short \
    and not rps.play_complete:
        rps.player_prev()
    
    elif event.key == InputKey.Ok \
    and event.key_type == InputType.Short:
        if rps.play_complete:
            rps.reset()
        else:
            rps.play()

    flipper.update_view()


@flipper.draw_callback()
def draw_callback(canvas: Canvas):
    canvas.draw_str_align_center(24, 12, "Bot")
    canvas.draw_str_align_center(104, 12, "You")

    canvas.draw_str_align_center(64, 12, f'[{rps.opponent_score} | {rps.player_score}]')
    canvas.draw_str_align_center(64, 32, "<- VS ->")

    canvas.draw_rframe(10, 18, 28, 28, 8)
    canvas.draw_icon(14, 22, rps.opponent)

    canvas.draw_rframe(90, 18, 28, 28, 8)
    canvas.draw_icon(94, 22, rps.player)


flipper.open_serial()
flipper.event_loop()

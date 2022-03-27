from launchcontrol_xl import INPUT
from pulse_tracker import PulseTracker

class Clock:
    def __init__(self, launch_control):
        self._launch_control = launch_control

        self._quarter = 0
        self._track_quarter_note = PulseTracker(24) # 24PPQN
        self._track_quarter_note.on_divisor(self._handle_quarter_note)

        self._bar = 0
        self._track_bar = PulseTracker(4) # 4 quarter notes to a bar
        self._track_bar.on_divisor(self._handle_bar)

    def clock_pulse(self):
        self._track_quarter_note.clock_pulse()

    def reset(self):
        self._track_quarter_note.reset()

    def _handle_quarter_note(self, count, reset):
        self._quarter += 1
        if reset:
            self._quarter = 0
            self._track_bar.reset()
        else:
            self._track_bar.clock_pulse()

        self._draw()

    def _handle_bar(self, count, reset):
        self._bar += 1
        if reset:
            self._bar = 0

    # Bars light up in pairs
    # 0 UP, 1 UP DOWN, 2 LEFT, 3 LEFT RIGHT
    # Quarter note lights up by itself from bottom to top
    def _draw(self):
        active_quarter = self._quarter % 4
        active_bar = self._bar % 4
        led_status = [
            (INPUT.BUTTON_UP, active_bar < 2),
            (INPUT.BUTTON_DOWN, active_bar == 1),
            (INPUT.BUTTON_LEFT, active_bar > 1),
            (INPUT.BUTTON_RIGHT, active_bar == 3),
            (INPUT.BUTTON_REC, active_quarter == 0),
            (INPUT.BUTTON_SOLO, active_quarter == 1),
            (INPUT.BUTTON_MUTE, active_quarter == 2),
            (INPUT.BUTTON_DEVICE, active_quarter == 3),
        ]
        self._launch_control.switch_side_buttons(led_status)

from pulse_tracker import PulseTracker
from launchpad_mini import COLOUR_GREEN, COLOUR_RED, BRIGHTNESS_LOW, BRIGHTNESS_HIGH

class Clock:
    def __init__(self):
        self._quarter = True
        self._bar = 0
        self._phrase = 0

        self._track_eight_note = PulseTracker(12) # 24PPQN
        self._track_eight_note.on_divisor(self._handle_eight_note)

        self._track_quarter_note = PulseTracker(2) # 2 eight notes to a quarter note
        self._track_quarter_note.on_divisor(self._handle_quarter_note)

        self._track_bar = PulseTracker(4) # 4 quarter notes to a bar
        self._track_bar.on_divisor(self._handle_bar)

        self._track_phrase = PulseTracker(4) # 4 bars to a phrase
        self._track_phrase.on_divisor(self._handle_phrase)

    def clock_pulse(self):
        self._track_eight_note.trigger_pulse()

    def reset(self):
        self._track_eight_note.reset_pulse()

    def _handle_eight_note(self, count, reset):
        self._quarter = False
        if reset:
            self._track_quarter_note.reset_pulse()
        else:
            self._track_quarter_note.trigger_pulse()

    def _handle_quarter_note(self, count, reset):
        self._quarter = True
        if reset:
            self._track_bar.reset_pulse()
        else:
            self._track_bar.trigger_pulse()

    def _handle_bar(self, count, reset):
        self._bar += 1
        if reset:
            self._track_phrase.reset_pulse()
        else:
            self._track_phrase.trigger_pulse()

    def _handle_phrase(self, count, reset):
        self._bar = 0
        self._phrase += 1

    def draw(self):
        brightness = BRIGHTNESS_LOW
        if self._quarter:
            brightness = BRIGHTNESS_HIGH

        colour = COLOUR_GREEN
        if self._phrase % 2 == 1:
            colour = COLOUR_RED

        state = []
        for i in range(0, self._bar):
            state.append((colour, BRIGHTNESS_LOW))
        state.append((colour, brightness))

        return state

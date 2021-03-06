import math
from pulse_tracker import PulseTracker
from launchpad_mini import COLOUR_GREEN, COLOUR_ORANGE, COLOUR_RED, COLOUR_OFF, BRIGHTNESS_LOW, BRIGHTNESS_HIGH

EUCLIDIAN = 0
REV_EUCLIDIAN = 1
MANUAL = 2

MAX_LENGTH = 16
MAX_OFFSET = MAX_LENGTH - 1

CHAN_MIN = 2
CHAN_MAX = 16
CHAN_DEFAULT = 10
NOTE_MIN = 0
NOTE_MAX = 127
NOTE_DEFAULT = 35

class Sequencer:
    def __init__(self, index, _on_trigger, state=''):
        self._index = index
        self._position = 0
        self._playback_pattern = []
        self._on_trigger = _on_trigger
        self._steps = PulseTracker(6)
        self._steps.on_divisor(self._handle_step)

        self._load_from_state(state)
        self._generate_sequence()

    def _generate_sequence(self):
        if self._mode is EUCLIDIAN:
            self._pattern = self._generate_euclidian()
            self._apply_offset()
        elif self._mode is REV_EUCLIDIAN:
            self._pattern = self._generate_rev_euclidian()
            self._apply_offset()
        elif self._mode is MANUAL:
            self._pattern = self._playback_pattern or self._pattern
            if len(self._pattern) < MAX_LENGTH:
                self._pattern.extend([0] * (MAX_LENGTH - len(self._pattern)))
            self._playback_pattern = self._pattern

    def _generate_euclidian(self):
        pulses = int(math.floor(float(self._length) / 100 * self._fill))
        steps = self._length

        if pulses == 0:
            return [0] * steps

        pattern = []
        counts = []
        remainders = []
        divisor = steps - pulses
        remainders.append(pulses)
        level = 0
        while True:
            counts.append(divisor // remainders[level])
            remainders.append(divisor % remainders[level])
            divisor = remainders[level]
            level = level + 1
            if remainders[level] <= 1:
                break
        counts.append(divisor)
        
        def build(level):
            if level == -1:
                pattern.append(0)
            elif level == -2:
                pattern.append(1)         
            else:
                for i in range(0, counts[level]):
                    build(level - 1)
                if remainders[level] != 0:
                    build(level - 2)
        
        build(level)
        i = pattern.index(1)
        pattern = pattern[i:] + pattern[0:i]
        return pattern

    def _generate_rev_euclidian(self):
        # TODO
        return [0] * self._length

    def _apply_offset(self):
        self._playback_pattern = self._pattern.copy()
        for i in range(0, self._offset):
            lastStep = self._playback_pattern.pop()
            self._playback_pattern.insert(0, lastStep)

    #region Control inputs
    def change_mode(self, mode):
        self._mode = mode
        self._generate_sequence()
    
    def toggle_mute(self):
        self.mute = not self.mute

    def set_mute(self, mute):
        self.mute = mute

    def _change_length(self, length):
        self._length = length
        self._generate_sequence()

    def increment_length(self):
        new_length = min(self._length + 1, MAX_LENGTH)
        if new_length != self._length:
            self._change_length(new_length)

    def decrement_length(self):
        new_length = max(1, self._length - 1)
        if new_length != self._length:
            self._change_length(new_length)

    def _set_fill(self, fill):
        self._fill = fill
        self._generate_sequence()

    def increment_fill(self):
        pulses = int(math.floor(float(self._length) / 100 * self._fill))
        new_pulses = min(pulses + 1, self._length)
        new_fill = int(math.ceil(float(new_pulses) / float(self._length) * 100))
        if new_fill != self._fill:
            self._set_fill(new_fill)

    def decrement_fill(self):
        pulses = int(math.floor(float(self._length) / 100 * self._fill))
        new_pulses = max(0, pulses - 1)
        new_fill = int(math.ceil(float(new_pulses) / float(self._length) * 100))
        if new_fill != self._fill:
            self._set_fill(new_fill)

    def _change_offset(self, offset):
        self._offset = offset
        self._apply_offset()

    def increment_offset(self):
        new_offset = min(self._offset + 1, self._length - 1)
        if new_offset != self._offset:
            self._change_offset(new_offset)

    def decrement_offset(self):
        new_offset = max(0, self._offset - 1)
        if new_offset != self._offset:
            self._change_offset(new_offset)

    def increment_channel(self):
        new_channel = min(self._channel + 1, CHAN_MAX)
        if new_channel != self._channel:
            self._channel = new_channel
            self._trigger(True)

    def decrement_channel(self):
        new_channel = max(CHAN_MIN, self._channel - 1)
        if new_channel != self._channel:
            self._channel = new_channel
            self._trigger(True)

    def change_note(self, delta):
        new_note = max(NOTE_MIN, min(self._note + delta, NOTE_MAX))
        if new_note != self._note:
            self._note = new_note
            self._trigger(True)

    def manual_input(self, step):
        if self._mode is MANUAL:
            if self._pattern[step] == 0:
                self._pattern[step] = 1
            else:
                self._pattern[step] = 0

    #region Timing inputs
    def clock_pulse(self):
        self._steps.clock_pulse()
    
    def _handle_step(self, count, reset):
        if reset:
            self._position = 0
        else:
            self._position += 1
            if self._position >= self._length:
                self._position = 0

        self._trigger()

    def reset(self):
        self._steps.reset()

    #region Outputs
    def _trigger(self, preview = False):
        if preview:
            self._on_trigger(self._index, self._channel, self._note)
            return

        if self.mute:
            return
        if self._playback_pattern[self._position] == 1:
            self._on_trigger(self._index, self._channel, self._note)

    def draw(self):
        state = []
        for i in range(0, MAX_LENGTH):
            colour = COLOUR_ORANGE
            brightness = BRIGHTNESS_LOW
            if i >= self._length:
                colour = COLOUR_RED
                if self._mode is MANUAL and self._playback_pattern[i] == 1:
                    brightness = BRIGHTNESS_HIGH
            else:
                if i == self._position:
                    colour = COLOUR_GREEN
                if self._playback_pattern[i] == 1:
                    brightness = BRIGHTNESS_HIGH
            state.append((colour, brightness))
        return state

    def draw_settings(self):
        state = []
        for mode in [(EUCLIDIAN, COLOUR_GREEN), (REV_EUCLIDIAN, COLOUR_ORANGE), (MANUAL, COLOUR_RED)]:
            if self._mode is mode[0]:
                state.append((mode[1], BRIGHTNESS_HIGH))
            else:
                state.append((mode[1], BRIGHTNESS_LOW))
        for bit in [16, 8, 4, 2, 1]:
            if self._channel & bit == bit:
                state.append((COLOUR_ORANGE, BRIGHTNESS_HIGH))
            else:
                state.append((COLOUR_ORANGE, BRIGHTNESS_LOW))
        state.append((COLOUR_OFF, BRIGHTNESS_LOW))
        for bit in [64, 32, 16, 8, 4, 2, 1]:
            if self._note & bit == bit:
                state.append((COLOUR_GREEN, BRIGHTNESS_HIGH))
            else:
                state.append((COLOUR_GREEN, BRIGHTNESS_LOW))
        return state

    #region Persistence
    def get_save_state(self):
        state_string = ''
        state_string += str(self._mode)
        state_string += '|'
        state_string += str(self._channel)
        state_string += '|'
        state_string += str(self._note)
        state_string += '|'
        if self.mute:
            state_string += '1'
        else :
            state_string += '0'
        state_string += '|'
        state_string += str(self._length)
        state_string += '|'
        state_string += str(self._fill)
        state_string += '|'
        state_string += str(self._offset)
        state_string += '|'
        state_string += ','.join(map(str, self._pattern))
        return state_string

    def _load_from_state(self, state):
        if not state:
            self._restore_defaults()
            return
        else:
            try:
                state_parts = state.split('|')
                if len(state_parts) != 8:
                    self._restore_defaults()
                    return
                # Mode
                try:
                    mode = int(state_parts[0])
                    if mode == MANUAL:
                        self._mode = MANUAL
                    elif mode == REV_EUCLIDIAN:
                        self._mode = REV_EUCLIDIAN
                    else:
                        self._mode = EUCLIDIAN
                except:
                    self._mode = EUCLIDIAN
                # Channel
                try:
                    channel = int(state_parts[1])
                    if channel >= CHAN_MIN  and channel <= CHAN_MAX:
                        self._channel = channel
                    else:
                        self._channel = CHAN_DEFAULT
                except:
                    self._channel = CHAN_DEFAULT
                # Note
                try:
                    note = int(state_parts[2])
                    if note >= NOTE_MIN and note <= NOTE_MAX:
                        self._note = note
                    else:
                        self._note = NOTE_DEFAULT
                except:
                    self._note = NOTE_DEFAULT
                # Mute
                self.mute = state_parts[3] == '1'
                # Length
                try:
                    length = int(state_parts[4])
                    if length > 0 and length <= MAX_LENGTH:
                        self._length = length
                    else:
                        self._length = MAX_LENGTH
                except:
                    self._length = MAX_LENGTH
                # Fill
                try:
                    fill = int(state_parts[5])
                    if fill >= 0 and fill <= 100:
                        self._fill = fill
                    else:
                        self._fill = 0
                except:
                    self._offset = 0
                # Offset
                try:
                    offset = int(state_parts[6])
                    if offset >= 0 and offset <= MAX_OFFSET:
                        self._offset = offset
                    else:
                        self._offset = 0
                except:
                    self._offset = 0
                # Pattern
                try:
                    raw_pattern = state_parts[7].split(',')
                    pattern = []
                    for step in raw_pattern:
                        if step == '1':
                            pattern.append(1)
                        else:
                            pattern.append(0)
                    self._pattern = pattern
                except:
                    self._pattern = [0] * self._length
            except:
                self._restore_defaults()

    def _restore_defaults(self):
        self._mode = EUCLIDIAN
        self._channel = CHAN_DEFAULT
        self._note = NOTE_DEFAULT
        self.mute = False
        self._length = MAX_LENGTH
        self._fill = 0
        self._offset = 0
        self._pattern = [0] * 16

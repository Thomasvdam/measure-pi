import math
from pulse_tracker import PulseTracker
from launchpad_mini import COLOUR_GREEN, COLOUR_ORANGE, COLOUR_RED, BRIGHTNESS_LOW, BRIGHTNESS_HIGH

EUCLIDIAN = 0
REV_EUCLIDIAN = 1
MANUAL = 2

MAX_LENGTH = 16
MAX_OFFSET = MAX_LENGTH - 1

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

    def change_length(self, length):
        self._length = length
        self._generate_sequence()

    def increment_length(self):
        new_length = min(self._length + 1, MAX_LENGTH)
        if new_length != self._length:
            self.change_length(new_length)

    def decrement_length(self):
        new_length = max(1, self._length - 1)
        if new_length != self._length:
            self.change_length(new_length)

    def set_fill(self, fill):
        self._fill = fill
        self._generate_sequence()

    def change_fill(self, delta):
        new_fill = max(0, min(self._fill + delta, 100))
        if new_fill != self._fill:
            self.set_fill(new_fill)

    def change_offset(self, offset):
        self._offset = offset
        self._apply_offset()

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
    def _trigger(self):
        if self.mute:
            return
        if self._playback_pattern[self._position] == 1:
            self._on_trigger(self._index)

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

    #region Persistence
    def get_save_state(self):
        state_string = ''
        state_string += str(self._mode)
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
                if len(state_parts) != 6:
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
                # Mute
                self.mute = state_parts[1] == '1'
                # Length
                try:
                    length = int(state_parts[2])
                    if length > 0 and length <= MAX_LENGTH:
                        self._length = length
                    else:
                        self._length = MAX_LENGTH
                except:
                    self._length = MAX_LENGTH
                # Fill
                try:
                    fill = int(state_parts[3])
                    if fill >= 0 and fill <= 100:
                        self._fill = fill
                    else:
                        self._fill = 0
                except:
                    self._offset = 0
                # Offset
                try:
                    offset = int(state_parts[4])
                    if offset >= 0 and offset <= MAX_OFFSET:
                        self._offset = offset
                    else:
                        self._offset = 0
                except:
                    self._offset = 0
                # Pattern
                try:
                    raw_pattern = state_parts[5].split(',')
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
        self.mute = False
        self._length = MAX_LENGTH
        self._fill = 0
        self._offset = 0
        self._pattern = [0] * 16

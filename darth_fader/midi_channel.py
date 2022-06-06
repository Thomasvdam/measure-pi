from launchcontrol_xl import INPUT, COLOUR

DEFAULT_VALUE = 0
DEFAULT_OFFSET = 0
DEFAULT_RANGE_MAX = 127

LATCH_THRESHOLD = 2
MIDI_CHANNEL_OUT = 1

class MidiChannel:
    def __init__(self, midi_out, launch_control, control, state_string):
        self._midi_out = midi_out
        self._launch_control = launch_control
        self._control = control

        self._momentary_on = False
        # Best to assume pots/sliders have changed
        self._momentary_latched = False
        self._momentary_value = 0

        self._load_from_state_string(state_string)

    def toggle_momentary(self, on):
        self._momentary_on = on
        if self._momentary_on:
            self._momentary_value = self._value
        else:
            self._momentary_latched = False
            self._check_latching()
            self.update_leds(self._get_led_colour())
            self.emit_value(self._momentary_value)

    def update_offset(self, new_offset):
        self._offset = max(0, min(127, new_offset))
        self.emit_value(self._value)

    def update_range_max(self, new_range_max):
        self._range_max = max(1, min(127, new_range_max))
        self.emit_value(self._value)

    def update_value(self, new_value):
        self._value = new_value
        self._check_latching()
        self.update_leds(self._get_led_colour())
        self.emit_value(self._value)

    def emit_value(self, value = None):
        if not self._momentary_latched:
            return

        value = self._value if value is None else value

        percentage = value / 127
        base_value = round(percentage * self._range_max)
        offset_value = min(127, self._offset + base_value)
        self._midi_out.send_message([176 + MIDI_CHANNEL_OUT, self._control, offset_value])

    # TODO rework this to a 'state' when introducing automation lanes
    def _get_led_colour(self):
        if self._momentary_latched:
            if not self._momentary_on:
                return COLOUR.OFF
            else:
                colour = COLOUR.AMBER if self._value != self._momentary_value else COLOUR.OFF
                return colour
        colour = COLOUR.RED if self._value < self._momentary_value else COLOUR.GREEN
        return colour

    def _check_latching(self):
        if self._momentary_latched:
            return

        latch_value = self._momentary_value
        if abs(latch_value - self._value) < LATCH_THRESHOLD:
            self._momentary_latched = True

    def update_leds(self, colour):
        print('Up to the inheriting class to implement. Poor design but whatever.')

    # State string format:
    # <value>,<offset>,<range_max>
    # Leaving room for automation lanes with | separator
    def get_save_state(self):
        return '{},{},{}'.format(self._value, self._offset, self._range_max)

    def _load_from_state_string(self, state_string):
        if not state_string:
            self._set_default_state()
            return
        try:
            state_parts = state_string.split('|')
            if len(state_parts) != 1:
                raise ValueError('Invalid state string')

            base_values = state_parts[0].split(',')
            value = int(base_values[0])
            if value < 0 or value > 127:
                self._value = DEFAULT_VALUE
            else:
                self._value = value

            offset = int(base_values[1])
            if offset < 0 or offset > 127:
                self._offset = DEFAULT_OFFSET
            else:
                self._offset = offset

            range_max = int(base_values[2])
            if range_max < 1 or range_max > 127:
                self._range_max = DEFAULT_RANGE_MAX
            else:
                self._range_max = range_max
        except:
            self._set_default_state()

    def _set_default_state(self):
        self._value = DEFAULT_VALUE
        self._offset = DEFAULT_OFFSET
        self._range_max = DEFAULT_RANGE_MAX

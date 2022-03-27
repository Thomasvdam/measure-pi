from launchcontrol_xl import INPUT

DEFAULT_VALUE = 0
DEFAULT_OFFSET = 0
DEFAULT_RANGE_MAX = 127

class MidiChannel:
    def __init__(self, midi_out, launch_control, control, state_string):
        self._midi_out = midi_out
        self._launch_control = launch_control
        self._control = control

        self._load_from_state_string(state_string)

    def update_offset(self, new_offset):
        self._offset = max(0, min(127, new_offset))
        self.emit_value()

    def update_range_max(self, new_range_max):
        self._range_max = max(1, min(127, new_range_max))
        self.emit_value()

    def update_value(self, value):
        self._value = value
        self.emit_value()

    def emit_value(self):
        percentage = self._value / 127
        base_value = round(percentage * self._range_max)
        value = min(127, self._offset + base_value)
        self._midi_out.send_message([183, self._control, value])

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

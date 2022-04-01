from launchcontrol_xl import INPUT
from midi_channel import MidiChannel

class SingleKnobChannel(MidiChannel):
    def __init__(self, midi_out, launch_control, control, state_string = ''):
        super(SingleKnobChannel, self).__init__(midi_out, launch_control, control, state_string)
        self._state = 0
        self._column = control % 8

    def update_leds(self, state):
        if state == self._state:
            return
        self._state = state
        self._launch_control.set_column_leds([((INPUT.KNOB_1, self._column), self._state)])

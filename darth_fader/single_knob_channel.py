from midi_channel import MidiChannel

class SingleKnobChannel(MidiChannel):
    def __init__(self, midi_out, launch_control, control, state_string = ''):
        super(SingleKnobChannel, self).__init__(midi_out, launch_control, control, state_string)

from midi_channel import MidiChannel

class FaderChannel(MidiChannel):
    def __init__(self, midi_out, launch_control, control, state_string = ''):
        super(FaderChannel, self).__init__(midi_out, launch_control, control, state_string)

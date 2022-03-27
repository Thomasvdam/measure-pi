class INPUT:
    NONE = -1
    KNOB_1 = 0
    KNOB_2 = 1
    KNOB_3 = 2
    FADER = 3
    BUTTON_1 = 4
    BUTTON_2 = 5
    BUTTON_UP = 6
    BUTTON_DOWN = 7
    BUTTON_LEFT = 8
    BUTTON_RIGHT = 9
    BUTTON_DEVICE = 10
    BUTTON_MUTE = 11
    BUTTON_SOLO = 12
    BUTTON_REC = 13

ROW_MAP = {
    0: INPUT.KNOB_1,
    1: INPUT.KNOB_2,
    2: INPUT.KNOB_3,
    3: INPUT.FADER,
    4: INPUT.BUTTON_1,
    5: INPUT.BUTTON_2,
}

SIDE_BUTTON_MAP = {
    100: INPUT.BUTTON_UP,
    101: INPUT.BUTTON_DOWN,
    102: INPUT.BUTTON_LEFT,
    103: INPUT.BUTTON_RIGHT,
    104: INPUT.BUTTON_DEVICE,
    105: INPUT.BUTTON_MUTE,
    106: INPUT.BUTTON_SOLO,
    107: INPUT.BUTTON_REC,
}

SIDE_BUTTON_OUTPUT_MAP = {
    INPUT.BUTTON_DEVICE: 40,
    INPUT.BUTTON_MUTE: 41,
    INPUT.BUTTON_SOLO: 42,
    INPUT.BUTTON_REC: 43,
    INPUT.BUTTON_UP: 44,
    INPUT.BUTTON_DOWN: 45,
    INPUT.BUTTON_LEFT: 46,
    INPUT.BUTTON_RIGHT: 47,
}

COLUMN_OUTPUT_MAP = {
    INPUT.KNOB_1: 0,
    INPUT.KNOB_2: 1,
    INPUT.KNOB_3: 2,
    INPUT.BUTTON_1: 3,
    INPUT.BUTTON_2: 4,
}

# Column LEDs are indexed 0-39 left to right, top to bottom
def get_column_output(control, column):
    return COLUMN_OUTPUT_MAP[control] * 8 + column

TEMPLATE_INDEX = 7
SYSEX_PREFIX = [240, 0, 32, 41, 2, 17, 120, TEMPLATE_INDEX]
SYSEX_SUFFIX = [247]

def construct_sysex_message(data):
    return SYSEX_PREFIX + data + SYSEX_SUFFIX

class LaunchControlXL:
    def __init__(self, midi_in, midi_out):
        self._midi_in = midi_in
        self._midi_out = midi_out

    def reset(self):
        self._midi_out.send_message([176 + TEMPLATE_INDEX, 0, 0])

    def message_to_input(self, message):
        channel = message[0]
        cc = message[1]
        velocity = message[2]

        if channel != 176:
            return (INPUT.NONE, None, None)

        if cc >= 100:
            return (SIDE_BUTTON_MAP[cc], None, velocity)

        row = cc // 8
        column = cc % 8
        return (ROW_MAP[row], column, velocity)

    def switch_side_buttons(self, buttons):
        button_message = []
        for button, on in buttons:
            value = 127 if on else 0
            button_message.extend([SIDE_BUTTON_OUTPUT_MAP[button], value])
        self._midi_out.send_message(construct_sysex_message(button_message))

    def set_column_leds(self, controls):
        led_message = []
        for control, colour in controls:
            control_type, column = control
            led_message.extend([get_column_output(control_type, column), colour])
        self._midi_out.send_message(construct_sysex_message(led_message))
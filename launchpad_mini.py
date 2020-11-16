COLOUR_OFF = 0
COLOUR_RED = 3
COLOUR_GREEN = 48
COLOUR_ORANGE = 51

BRIGHTNESS_LOW = 17
BRIGHTNESS_MEDIUM = 34
BRIGHTNESS_HIGH = 51

RESET_MESSAGE = [176, 0, 0]

GRID = [
    [[144, 0], [144, 16], [144, 32], [144, 48], [144, 64], [144, 80], [144, 96], [144, 112]],
    [[144, 1], [144, 17], [144, 33], [144, 49], [144, 65], [144, 81], [144, 97], [144, 113]],
    [[144, 2], [144, 18], [144, 34], [144, 50], [144, 66], [144, 82], [144, 98], [144, 114]],
    [[144, 3], [144, 19], [144, 35], [144, 51], [144, 67], [144, 83], [144, 99], [144, 115]],
    [[144, 4], [144, 20], [144, 36], [144, 52], [144, 68], [144, 84], [144, 100], [144, 116]],
    [[144, 5], [144, 21], [144, 37], [144, 53], [144, 69], [144, 85], [144, 101], [144, 117]],
    [[144, 6], [144, 22], [144, 38], [144, 54], [144, 70], [144, 86], [144, 102], [144, 118]],
    [[144, 7], [144, 23], [144, 39], [144, 55], [144, 71], [144, 87], [144, 103], [144, 119]],
]

class LaunchpadMini:
    def __init__(self, midi_in, midi_out):
        self._midi_in = midi_in
        self._midi_out = midi_out

    def turn_pad_on(self, location, colour, brightness=BRIGHTNESS_LOW):
        x, y = location
        self._midi_out.send_message(GRID[x][y] + [colour & brightness])
    
    def turn_pad_off(self, location):
        x, y = location
        self._midi_out.send_message(GRID[x][y] + [COLOUR_OFF])

    def turn_all_pads_off(self):
        self._midi_out.send_message(RESET_MESSAGE)

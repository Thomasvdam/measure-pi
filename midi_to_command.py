import math
from sequencer import EUCLIDIAN, REV_EUCLIDIAN, MANUAL

class CONTROL_MODE:
    DEFAULT = 0
    SETTINGS = 1

class COMMAND:
    CHANGE_SEQUENCE = 0
    TOGGLE_MUTE = 1
    SET_MUTE = 2
    CHANGE_MODE = 3
    MANUAL_INPUT = 4
    BOOT_COMBO = 5

BOOT_COMBO = [0, 112, 7, 119]

BSP_MUTE_TOGGLES = [20, 22, 24, 26, 28, 30, 52, 53]

def map_midi_to_command(message, mode = CONTROL_MODE.DEFAULT):
    # BSP toggles
    if message[0] == 176 and message[1] in BSP_MUTE_TOGGLES:
        index = BSP_MUTE_TOGGLES.index(message[1])
        return (COMMAND.SET_MUTE, (index, message[2] == 127))
    # LP top row keydown
    if message[0] == 176 and message[2] == 127 and message[1] >= 104 and message[1] <= 111:
        new_index = message[1] - 104
        return (COMMAND.CHANGE_SEQUENCE, (new_index,))
    # LP right column, top row keyup
    if message[0] == 128 and message[2] == 64 and message[1] == 8:
        return (COMMAND.TOGGLE_MUTE, None)
    # LP right column, 2nd row keydown
    if message[0] == 144 and message[2] == 127 and message[1] == 24:
        return (COMMAND.CHANGE_MODE, (EUCLIDIAN,))
    # LP right column, 3rd row keydown
    if message[0] == 144 and message[2] == 127 and message[1] == 40:
        return (COMMAND.CHANGE_MODE, (REV_EUCLIDIAN,))
    # LP right column, 4th row keydown
    if message[0] == 144 and message[2] == 127 and message[1] == 56:
        return (COMMAND.CHANGE_MODE, (MANUAL,))
    if message[1] in BOOT_COMBO:
        x = message[1] % 16
        y = math.floor(message[1] / 16)
        # 144 is note on, 127 is note off
        return (COMMAND.BOOT_COMBO, ((x, y), message[0] == 144))
    # LP buttons for manual input
    if message[0] == 144 and message[2] == 127 and message[1] >= 0 and message[1] <= 120:
        if mode is CONTROL_MODE.DEFAULT:
            x = message[1] % 16
            y = math.floor(message[1] / 16)
            return (COMMAND.MANUAL_INPUT, (x, y))

    print(message)
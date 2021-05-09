import math
from sequencer import EUCLIDIAN, REV_EUCLIDIAN, MANUAL

class CONTROL_MODE:
    DEFAULT = 0
    SETTINGS = 1

class COMMAND:
    NONE = -1
    CHANGE_SEQUENCE = 0
    CHANGE_CONTROL_MODE = 1
    TOGGLE_MUTE = 2
    SET_MUTE = 3
    CHANGE_MODE = 4
    MANUAL_INPUT = 5
    CHANGE_LENGTH_INC = 6
    CHANGE_LENGTH_DEC = 7
    CHANGE_FILL = 8
    CHANGE_OFFSET_INC = 9
    CHANGE_OFFSET_DEC = 10
    CHANGE_CHANNEL_INC = 100
    CHANGE_CHANNEL_DEC = 101
    CHANGE_NOTE_REL = 102
    BOOT_COMBO = 1337

BOOT_COMBO = [0, 112, 7, 119]

BSP_TOP_KNOBS = [10, 74, 71, 76, 77, 93, 73, 75]
BSP_BOTTOM_KNOBS = [114, 18, 19, 16, 17, 91, 79, 72]
BSP_MUTE_TOGGLES = [20, 22, 24, 26, 28, 30, 52, 54]
BSP_SELECT_BUTTONS = [21, 23, 25, 27, 29, 31, 53, 55]

class MidiToControl:
    def __init__(self):
        self._mod_down = False

    def map_midi_to_command(self, message, mode = CONTROL_MODE.DEFAULT):
        # Sequence selection is mode agnostic
        if message[0] == 176 and message[1] in BSP_SELECT_BUTTONS:
            new_index = BSP_SELECT_BUTTONS.index(message[1])
            return (COMMAND.CHANGE_SEQUENCE, (new_index,))
        if mode is CONTROL_MODE.DEFAULT:
            return self.map_midi_to_default_command(message)
        elif mode is CONTROL_MODE.SETTINGS:
            return self.map_midi_to_settings_command(message)

    def map_midi_to_default_command(self, message):
        # BSP top left pad
        if (message[0] == 144 or message[0] == 128) and message[1] == 44:
            self._mod_down = message[0] == 144
            return (COMMAND.NONE, None)
        # BSP knobs
        if message[0] == 176 and message[1] in BSP_TOP_KNOBS:
            index = BSP_TOP_KNOBS.index(message[1])
            if message[2] == 64:
                return (COMMAND.NONE, None)
            if self._mod_down:
                if message[2] > 64:
                    return (COMMAND.CHANGE_OFFSET_INC, (index,))
                if message[2] < 64:
                    return (COMMAND.CHANGE_OFFSET_DEC, (index,))
            else:
                return (COMMAND.CHANGE_FILL, (index, message[2] - 64))
        if message[0] == 176 and message[1] in BSP_BOTTOM_KNOBS:
            index = BSP_BOTTOM_KNOBS.index(message[1])
            if message[2] == 64:
                return (COMMAND.NONE, None)
            if message[2] > 64:
                return (COMMAND.CHANGE_LENGTH_INC, (index,))
            if message[2] < 64:
                return (COMMAND.CHANGE_LENGTH_DEC, (index,))
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
            return (COMMAND.CHANGE_CONTROL_MODE, (CONTROL_MODE.SETTINGS,))
        if message[1] in BOOT_COMBO:
            x = message[1] % 16
            y = math.floor(message[1] / 16)
            # 144 is note on, 127 is note off
            return (COMMAND.BOOT_COMBO, ((x, y), message[0] == 144))
        # LP buttons for manual input
        if message[0] == 144 and message[2] == 127 and message[1] >= 0 and message[1] <= 120:
            x = message[1] % 16
            y = math.floor(message[1] / 16)
            return (COMMAND.MANUAL_INPUT, (x, y))

        return (COMMAND.NONE, None)

    def map_midi_to_settings_command(self, message):
        # BSP knobs
        if message[0] == 176 and message[1] in BSP_TOP_KNOBS:
            index = BSP_TOP_KNOBS.index(message[1])
            if message[2] == 64:
                return (COMMAND.NONE, None)
            if message[2] > 64:
                return (COMMAND.CHANGE_CHANNEL_INC, (index,))
            if message[2] < 64:
                return (COMMAND.CHANGE_CHANNEL_DEC, (index,))
        if message[0] == 176 and message[1] in BSP_BOTTOM_KNOBS:
            index = BSP_BOTTOM_KNOBS.index(message[1])
            if message[2] == 64:
                return (COMMAND.NONE, None)
            return (COMMAND.CHANGE_NOTE_REL, (index, message[2] - 64))
        # LP right column, 2nd row keydown
        if message[0] == 144 and message[2] == 127 and message[1] == 24:
            return (COMMAND.CHANGE_CONTROL_MODE, (CONTROL_MODE.DEFAULT,))
        if message[0] == 144 and message[2] == 127:
            if message[1] == 0:
                return (COMMAND.CHANGE_MODE, (EUCLIDIAN,))
            elif message[1] == 1:
                return (COMMAND.CHANGE_MODE, (REV_EUCLIDIAN,))
            elif message[1] == 2:
                return (COMMAND.CHANGE_MODE, (MANUAL,))

        return (COMMAND.NONE, None)

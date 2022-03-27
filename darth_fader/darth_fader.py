import threading
import time
import os
from rtmidi.midiconstants import TIMING_CLOCK, SONG_START, SONG_STOP, SONG_CONTINUE
from debounce import debounce
from clock import Clock
from launchcontrol_xl import LaunchControlXL, INPUT
from single_knob_channel import SingleKnobChannel
from fader_channel import FaderChannel

BOOT_COMBO = { INPUT.BUTTON_LEFT, INPUT.BUTTON_RIGHT, INPUT.BUTTON_UP, INPUT.BUTTON_DOWN }
class PARSING_TYPE:
    NONE = 0
    SIMPLE = 1
    FADER = 2

class DarthFader(threading.Thread):
    def __init__(self, midi_in, midi_out):
        super(DarthFader, self).__init__()
        self._midi_out = midi_out
        self._midi_in = midi_in
        # Clock messages are ignored by default
        midi_in.ignore_types(timing=False)
        midi_in.set_callback(self._handle_input)

        self._boot_combo = []
        self._reboot_set = False

        self._launch_control = LaunchControlXL(midi_in, midi_out)
        self._clock = Clock(self._launch_control)

        states = self._load_from_state()
        self._simple_channels = []
        for i in range(0, 8):
            self._simple_channels.append(SingleKnobChannel(midi_out, self._launch_control, i, states[PARSING_TYPE.SIMPLE][i]))
        
        self._fader_channels = []
        for i in range(0, 8):
            self._fader_channels.append(FaderChannel(midi_out, self._launch_control, 8 + i, states[PARSING_TYPE.FADER][i]))

        self.start()

    def _handle_boot_combo(self, button, velocity):
        if self._reboot_set:
            return

        if velocity > 0:
            self._boot_combo.append(button)
            if len(self._boot_combo) == 4:
                self._reboot_set = True
                self._launch_control.switch_side_buttons(map(lambda button : (button, True), self._boot_combo))
                print('Swapping config')
                os.system('sudo sh /home/pi/measure_pi/swap_config.sh')
        else:
            self._boot_combo.remove(button)
            self._launch_control.switch_side_button(button, False)

    def run(self):
        self.done = False

        self._launch_control.reset()
        self._clock.reset()
        self._write_save_state()

        while not self.done:
            time.sleep(0.02)

    def _handle_input(self, event, data=None):
        message, deltatime = event

        if message[0] is TIMING_CLOCK:
            self._clock.clock_pulse()
            return
        elif message[0] is SONG_START:
            self._clock.reset()
            return
        elif message[0] is SONG_STOP or message[0] is SONG_CONTINUE:
            return

        (input, column, value) = self._launch_control.message_to_input(message)

        if input is INPUT.NONE:
            return

        if input in BOOT_COMBO:
            self._handle_boot_combo(input, value)

        if input is INPUT.KNOB_1:
            self._simple_channels[column].update_value(value)
        elif input is INPUT.KNOB_2:
            self._fader_channels[column].update_range_max(value)
        elif input is INPUT.KNOB_3:
            self._fader_channels[column].update_offset(value)
        elif input is INPUT.FADER:
            self._fader_channels[column].update_value(value)

        self._write_save_state()

    # Loading and writing long term storage
    def _load_from_state(self):
        try:
            f = open('fader_state.txt', 'r')
            lines = f.readlines()
            states = {
                PARSING_TYPE.SIMPLE: [],
                PARSING_TYPE.FADER: [],
            }
            parsing_type = PARSING_TYPE.NONE

            first_line = lines.pop(0)
            if first_line != 'darth_fader:v1\n':
                raise Exception('Invalid file format')
            for line in lines:
                if line == 'simple_channels\n':
                    parsing_type = PARSING_TYPE.SIMPLE
                elif line == 'fader_channels\n':
                    parsing_type = PARSING_TYPE.FADER
                else:
                    states[parsing_type].append(line)
            f.close()

            return states
        except Exception as e:
            print(e)
            print('Invalid state file, resetting defaults')
            return {
                PARSING_TYPE.SIMPLE: [None] * 8,
                PARSING_TYPE.FADER: [None] * 8,
            }

    @debounce(1)
    def _write_save_state(self):
        self._write_save_state_raw()

    def _write_save_state_raw(self):
        state = 'darth_fader:v1\nsimple_channels'
        for simple_channel in self._simple_channels:
            state += '\n'
            state += simple_channel.get_save_state()
        
        state += '\nfader_channels'
        for fader_channel in self._fader_channels:
            state += '\n'
            state += fader_channel.get_save_state()   

        f = open('fader_state.txt', 'w')
        f.write(state)
        f.close()
import threading
import time
import os
from rtmidi.midiconstants import TIMING_CLOCK, SONG_START, SONG_STOP, SONG_CONTINUE
from midi_to_command import MidiToControl, COMMAND, CONTROL_MODE
from launchpad_mini import LaunchpadMini, COLOUR_ORANGE, COLOUR_GREEN, COLOUR_RED, BRIGHTNESS_LOW, BRIGHTNESS_MEDIUM, BRIGHTNESS_HIGH
from clock import Clock
from debounce import debounce
from sequencer import Sequencer, EUCLIDIAN, REV_EUCLIDIAN, MANUAL

CIRCLE_COORDS = [
    (4, 0), (5, 1), (6, 2), (7, 3),
    (7, 4), (6, 5), (5, 6), (4, 7),
    (3, 7), (2, 6), (1, 5), (0, 4),
    (0, 3), (1, 2), (2, 1), (3, 0)
]

SETTINGS_COORDS = [
    (0,0), (1,0), (2,0), (3,0),
    (4,0), (5,0), (6,0), (7,0),
    (0,1), (1,1), (2,1), (3,1),
    (4,1), (5,1), (6,1), (7,1),
]

class Sequency(threading.Thread):
    def __init__(self, midi_in, midi_out):
        super(Sequency, self).__init__()
        self._midi_out = midi_out
        self._midi_in = midi_in
        # Clock messages are ignored by default
        midi_in.ignore_types(timing=False)
        midi_in.set_callback(self._handle_input)

        self._lp = LaunchpadMini(midi_in, midi_out)
        self._controller = MidiToControl()

        self._boot_combo = []
        self._reboot_set = False
        self._control_mode = CONTROL_MODE.DEFAULT

        sequence_states = self._load_from_state()

        self._clock = Clock()
        self._sequences = []
        self._active_sequence = 0
        for i in range(0, 8):
            self._sequences.append(Sequencer(i, self._on_trigger, sequence_states[i]))

        self.start()

    def run(self):
        self.done = False

        time.sleep(5)
        self._startup_animation()

        self._draw_active_sequence()
        self._draw()

        while not self.done:
            time.sleep(0.02)

    def kill(self):
        self._write_save_state_raw()
        self._lp.turn_all_pads_off()

    def _startup_animation(self):
        for colour in [COLOUR_RED, COLOUR_ORANGE, COLOUR_GREEN]:
            for brightness in [BRIGHTNESS_LOW, BRIGHTNESS_MEDIUM, BRIGHTNESS_HIGH]:
                for coords in CIRCLE_COORDS:
                    self._lp.turn_pad_on(coords, colour, brightness)
                    time.sleep(0.01)
        self._lp.turn_all_pads_off()

    def _get_sequence_colour(self, index):
        if self._sequences[index].mute:
            return COLOUR_RED
        elif index == self._active_sequence:
            return COLOUR_GREEN
        return COLOUR_ORANGE

    def _on_trigger(self, index, channel, note):
        self._midi_out.send_message([143 + channel, note, 64])
        bsp_lp = threading.Timer(0.06, self._end_trigger_bsp, [index, channel, note])
        bsp_lp.start()

        colour = self._get_sequence_colour(index)
        self._lp.turn_pad_on(('T', index), colour, BRIGHTNESS_HIGH)
        t_lp = threading.Timer(0.1, self._end_trigger_lp, [index])
        t_lp.start()
    
    def _end_trigger_lp(self, index):
        colour = self._get_sequence_colour(index)
        self._lp.turn_pad_on(('T', index), colour, BRIGHTNESS_LOW)

    def _end_trigger_bsp(self, index, channel, note):
        self._midi_out.send_message([127 + channel, note, 64])

    def _handle_input(self, event, data=None):
        message, deltatime = event
        if message[0] is TIMING_CLOCK:
            self._clock.clock_pulse()
            for seq in self._sequences:
                seq.clock_pulse()
        elif message[0] is SONG_START:
            self._clock.reset()
            for seq in self._sequences:
                seq.reset()
        elif message[0] is SONG_STOP or message[0] is SONG_CONTINUE:
            pass
        else:
            command = self._controller.map_midi_to_command(message, self._control_mode)
            self._handle_command(command)

        self._draw()

    def _handle_command(self, command):
        if not command:
            return

        command_type, args = command
        if command_type is COMMAND.NONE:
            return
        elif command_type is COMMAND.CHANGE_CONTROL_MODE:
            self._change_control_mode(args[0])
        elif command_type is COMMAND.CHANGE_SEQUENCE:
            self._change_active_sequence(args[0])
        elif command_type is COMMAND.TOGGLE_MUTE:
            self._toggle_mute()
        elif command_type is COMMAND.SET_MUTE:
            self._set_mute(args[0], args[1])
        elif command_type is COMMAND.CHANGE_MODE:
            self._change_sequence_mode(args[0])
        elif command_type is COMMAND.MANUAL_INPUT:
            self._input_manual_step(args)
        elif command_type is COMMAND.CHANGE_LENGTH_INC:
            self._increment_sequence_length(args[0])
        elif command_type is COMMAND.CHANGE_LENGTH_DEC:
            self._decrement_sequence_length(args[0])
        elif command_type is COMMAND.CHANGE_FILL_INC:
            self._increment_fill(args[0])
        elif command_type is COMMAND.CHANGE_FILL_DEC:
            self._decrement_fill(args[0])
        elif command_type is COMMAND.CHANGE_OFFSET_INC:
            self._increment_sequence_offset(args[0])
        elif command_type is COMMAND.CHANGE_OFFSET_DEC:
            self._decrement_sequence_offset(args[0])
        elif command_type is COMMAND.CHANGE_CHANNEL_INC:
            self._increment_sequence_channel(args[0])
        elif command_type is COMMAND.CHANGE_CHANNEL_DEC:
            self._decrement_sequence_channel(args[0])
        elif command_type is COMMAND.CHANGE_NOTE_REL:
            self._change_sequence_note(args[0], args[1])
        elif command_type is COMMAND.BOOT_COMBO:
            self._handle_boot_combo(args)
        else:
            print('Unkown command', command_type, args)

        self._write_save_state()

    def _change_active_sequence(self, index):
        self._active_sequence = index
        self._draw_active_sequence()

    def _change_control_mode(self, mode):
        self._control_mode = mode
        self._lp.turn_all_pads_off()
        self._draw_active_sequence()
        self._draw()

    def _toggle_mute(self):
        self._sequences[self._active_sequence].toggle_mute()
        self._draw_active_sequence()

    def _set_mute(self, index, mute):
        self._sequences[index].set_mute(mute)
        self._draw_active_sequence()

    def _change_sequence_mode(self, mode):
        active_sequence = self._sequences[self._active_sequence]
        active_sequence.change_mode(mode)
        self._draw_active_sequence()

    def _increment_sequence_length(self, index):
        self._active_sequence = index
        active_sequence = self._sequences[self._active_sequence]
        active_sequence.increment_length()
        self._draw_active_sequence()

    def _decrement_sequence_length(self, index):
        self._active_sequence = index
        active_sequence = self._sequences[self._active_sequence]
        active_sequence.decrement_length()
        self._draw_active_sequence()

    def _increment_fill(self, index):
        self._active_sequence = index
        active_sequence = self._sequences[self._active_sequence]
        active_sequence.increment_fill()
        self._draw_active_sequence()

    def _decrement_fill(self, index):
        self._active_sequence = index
        active_sequence = self._sequences[self._active_sequence]
        active_sequence.decrement_fill()
        self._draw_active_sequence()

    def _increment_sequence_offset(self, index):
        self._active_sequence = index
        active_sequence = self._sequences[self._active_sequence]
        active_sequence.increment_offset()
        self._draw_active_sequence()

    def _decrement_sequence_offset(self, index):
        self._active_sequence = index
        active_sequence = self._sequences[self._active_sequence]
        active_sequence.decrement_offset()
        self._draw_active_sequence()

    def _increment_sequence_channel(self, index):
        self._active_sequence = index
        active_sequence = self._sequences[self._active_sequence]
        active_sequence.increment_channel()
        self._draw_active_sequence()

    def _decrement_sequence_channel(self, index):
        self._active_sequence = index
        active_sequence = self._sequences[self._active_sequence]
        active_sequence.decrement_channel()
        self._draw_active_sequence()

    def _change_sequence_note(self, index, delta):
        self._active_sequence = index
        active_sequence = self._sequences[self._active_sequence]
        active_sequence.change_note(delta)
        self._draw_active_sequence()

    def _handle_boot_combo(self, key_event):
        if self._reboot_set:
            return

        key, on = key_event
        if on:
            self._boot_combo.append(key)
            if len(self._boot_combo) == 4:
                self._reboot_set = True
                for coords in self._boot_combo:
                    self._lp.turn_pad_on(coords, COLOUR_GREEN, BRIGHTNESS_HIGH)
                os.system('sudo sh /home/pi/measure_pi/swap_config.sh')
        else:
            self._boot_combo.remove(key)
            self._lp.turn_pad_off(key)


    def _input_manual_step(self, coords):
        if coords in CIRCLE_COORDS:
            step = CIRCLE_COORDS.index(coords)
            active_sequence = self._sequences[self._active_sequence]
            active_sequence.manual_input(step)

    def _draw_active_sequence(self):
        for i, sequence in enumerate(self._sequences):
            colour = COLOUR_ORANGE
            if sequence.mute:
                colour = COLOUR_RED
            if i == self._active_sequence:
                colour = COLOUR_GREEN
            self._lp.turn_pad_on(('T', i), colour)

        active_sequence = self._sequences[self._active_sequence]

        if active_sequence.mute:
            self._lp.turn_pad_on((8, 0), COLOUR_RED, BRIGHTNESS_HIGH)
        else:
            self._lp.turn_pad_off((8, 0))

        if active_sequence._mode is EUCLIDIAN:
            self._lp.turn_pad_on((8, 1), COLOUR_GREEN, BRIGHTNESS_HIGH)
        else:
            self._lp.turn_pad_off((8, 1))
        if active_sequence._mode is REV_EUCLIDIAN:
            self._lp.turn_pad_on((8, 2), COLOUR_GREEN, BRIGHTNESS_HIGH)
        else:
            self._lp.turn_pad_off((8, 2))
        if active_sequence._mode is MANUAL:
            self._lp.turn_pad_on((8, 3), COLOUR_GREEN, BRIGHTNESS_HIGH)
        else:
            self._lp.turn_pad_off((8, 3))

    def _draw(self):
        clock_state = self._clock.draw()
        for i, message in enumerate(clock_state):
            colour, brightness = message
            self._lp.turn_pad_on((8, 7 - i), colour, brightness)

        if self._control_mode is CONTROL_MODE.DEFAULT:
            self._draw_sequence()
        elif self._control_mode is CONTROL_MODE.SETTINGS:
            self._draw_settings()

    def _draw_sequence(self):
        active_sequence = self._sequences[self._active_sequence]
        sequence_state = active_sequence.draw()
        for i, message in enumerate(sequence_state):
            colour, brightness = message
            self._lp.turn_pad_on(CIRCLE_COORDS[i], colour, brightness)

    def _draw_settings(self):
        active_sequence = self._sequences[self._active_sequence]
        settings_state = active_sequence.draw_settings()
        for i, message in enumerate(settings_state):
            colour, brightness = message
            self._lp.turn_pad_on(SETTINGS_COORDS[i], colour, brightness)

    def _load_from_state(self):
        try:
            f = open('state.txt', 'r')
            lines = f.readlines()
            sequence_states = []
            parsing_sequences = False
            for line in lines:
                if parsing_sequences:
                    sequence_states.append(line)
                if line == 'seqs\n':
                    parsing_sequences = True

            f.close()

            # If somehow we're missing states fill up to 8
            sequence_states.extend([None] * (8 - len(sequence_states)))
            return sequence_states
        except:
            print('Invalid state file, resetting defaults')
            return [None] * 8

    @debounce(1)
    def _write_save_state(self):
        self._write_save_state_raw()

    def _write_save_state_raw(self):
        state = 'seqs'
        for seq in self._sequences:
            state += '\n'
            state += seq.get_save_state()

        f = open('state.txt', 'w')
        f.write(state)
        f.close()

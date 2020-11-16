from pulse_tracker import PulseTracker
from launchpad_mini import LaunchpadMini, COLOUR_ORANGE, COLOUR_GREEN, COLOUR_RED, BRIGHTNESS_LOW, BRIGHTNESS_MEDIUM, BRIGHTNESS_HIGH
from rtmidi.midiconstants import TIMING_CLOCK, SONG_START

class MeasurePi:
    def __init__(self, midi_in, midi_out):
        self._midi_in = midi_in
        # Clock messages are ignored by default
        midi_in.ignore_types(timing=False)
        midi_in.set_callback(self._handle_input)

        self._midi_out = midi_out

        self._lp = LaunchpadMini(midi_in, midi_out)

        self._pulse_quarter_notes = PulseTracker(24) # Direct MIDI pulses
        self._quarter_notes = [
            (4, 0), (5, 1), (6, 2), (7, 3),
            (7, 4), (6, 5), (5, 6), (4, 7),
            (3, 7), (2, 6), (1, 5), (0, 4),
            (0, 3), (1, 2), (2, 1), (3, 0)
        ];
        self._pulse_quarter_notes.on_divisor(self._handle_quarter_note)

        self._pulse_phrases = PulseTracker(16) # 16 quarter notes
        self._phrases = [(4, 3), (4, 4), (3, 4), (3, 3)]
        self._phrase_colour = COLOUR_GREEN
        self._pulse_phrases.on_divisor(self._handle_phrase)

        self._pulse_periods = PulseTracker(4) # 4 phrases
        self._periods = [
            [(4, 2), (5, 2), (5, 3)],
            [(5, 4), (5, 5), (4, 5)],
            [(3, 5), (2, 5), (2, 4)],
            [(2, 3), (2, 2), (3, 2)]
        ]
        self._pulse_periods.on_divisor(self._handle_period)

        # Reset visualisation
        self._lp.turn_all_pads_off()
        self._pulse_quarter_notes.reset_pulse()

    def _handle_input(self, event, data=None):
        message, deltatime = event
        if message[0] is TIMING_CLOCK:
            self._pulse_quarter_notes.trigger_pulse()
        elif message[0] is SONG_START:
            self._pulse_quarter_notes.reset_pulse()

    def _handle_quarter_note(self, note_number, reset):
        index = note_number % 16 # len(self._quarter_notes)
        # Reset all QN
        if index == 0:
            for location in self._quarter_notes:
                self._lp.turn_pad_off(location)
            self._lp.turn_pad_on(self._quarter_notes[index], COLOUR_ORANGE, BRIGHTNESS_HIGH)
        else:
            # Turn previous pad dim
            self._lp.turn_pad_on(self._quarter_notes[index - 1], COLOUR_ORANGE)
            self._lp.turn_pad_on(self._quarter_notes[index], COLOUR_ORANGE, BRIGHTNESS_HIGH)
        if reset:
            self._pulse_phrases.reset_pulse()
        else:
            self._pulse_phrases.trigger_pulse()

    def _handle_phrase(self, phrase_number, reset):
        index = phrase_number % 4 # len(self._phrases)
        if index == 0:
            # Green for antecendent, red for consequent
            if phrase_number % 8 == 0:
                self._phrase_colour = COLOUR_GREEN
            else:
                self._phrase_colour = COLOUR_RED
            for location in self._phrases:
                self._lp.turn_pad_off(location)
            self._lp.turn_pad_on(self._phrases[index], self._phrase_colour, BRIGHTNESS_HIGH)
        else:
            self._lp.turn_pad_on(self._phrases[index - 1], self._phrase_colour)
            self._lp.turn_pad_on(self._phrases[index], self._phrase_colour, BRIGHTNESS_HIGH)
        if reset:
            self._pulse_periods.reset_pulse()
        else:
            self._pulse_periods.trigger_pulse()

    def _handle_period(self, period_number, reset):
        index = period_number % 4 # len(self._periods)
        if index == 0:
            for locations in self._periods:
                for location in locations:
                    self._lp.turn_pad_off(location)
            for location in self._periods[index]:
                self._lp.turn_pad_on(location, self._phrase_colour, BRIGHTNESS_HIGH)
        else:
            for location in self._periods[index - 1]:
                self._lp.turn_pad_on(location, self._phrase_colour)
            for location in self._periods[index]:
                self._lp.turn_pad_on(location, self._phrase_colour, BRIGHTNESS_HIGH)
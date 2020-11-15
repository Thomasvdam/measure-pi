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
            (0, 4), (1, 5), (2, 6), (3, 7),
            (4, 7), (5, 6), (6, 5), (7, 4),
            (7, 3), (6, 2), (5, 1), (4, 0),
            (3, 0), (2, 1), (1, 2), (0, 3)
        ];
        self._pulse_quarter_notes.on_divisor(self._handle_quarter_note)

        self._pulse_phrases = PulseTracker(16) # 16 quarter notes
        self._phrases = [(3, 4), (4, 4), (4, 3), (3, 3)]
        self._phrase_colour = COLOUR_GREEN # Start with green
        self._pulse_phrases.on_divisor(self._handle_phrase)

        self._pulse_periods = PulseTracker(4) # 4 phrases
        self._periods = [COLOUR_GREEN, COLOUR_RED]
        self._pulse_periods.on_divisor(self._handle_period)

        # Reset visualisation
        self._lp.turn_all_pads_off()
        self._pulse_quarter_notes.reset_pulse()

    def _handle_input(self, event):
        message, deltatime = event
        if message[0] is TIMING_CLOCK:
            data._pulse_quarter_notes.trigger_pulse()
        elif message[0] is SONG_START:
            data._pulse_quarter_notes.reset_pulse()

    def _handle_quarter_note(self, note_number):
        index = note_number % 16 # len(self._quarter_notes)
        # Reset all QN
        if index == 0:
            for location in self._quarter_notes:
                self._lp.turn_pad_off(location)
            self._lp.turn_pad_on(self._quarter_notes[index], COLOR_ORANGE, BRIGHTNESS_HIGH)
        else:
            # Turn previous pad dim
            self._lp.turn_pad_on(self._quarter_notes[index - 1], COLOR_ORANGE)
            self._lp.turn_pad_on(self._quarter_notes[index], COLOR_ORANGE, BRIGHTNESS_HIGH)
        self._pulse_phrases.trigger_pulse()

    def _handle_phrase(self, phrase_number):
        # Trigger period first as the phrase colour might update
        self._pulse_periods.trigger_pulse()

        index = phrase_number % 4 # len(self._phrases)
        if index == 0:
            for location in self._phrases:
                self._lp.turn_pad_off(location)
            self._lp.turn_pad_on(self._phrases[index], self._phrase_colour, BRIGHTNESS_HIGH)
        else:
            self._lp.turn_pad_on(self._phrases[index - 1], self._phrase_colour)
            self._lp.turn_pad_on(self._phrases[index], self._phrase_colour, BRIGHTNESS_HIGH)
        
    def _handle_period(self, period_number):
        index = period_number % 2 # len(self._periods)
        self._phrase_colour = self._phrase[index]

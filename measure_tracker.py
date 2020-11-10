import math

# TODO: Periods? 1536 pulses. Usual cadence is weak > strong
class MeasureTracker:
    def __init__(self):
        self._pulse_count = 0
        self._quarter_note_observers = []
        self._phrase_observers = []

    def reset_pulse(self):
        self._pulse_count = 0

    def trigger_pulse(self):
        self._pulse_count += 1

        on_quarter_note = self._pulse_count % 24 == 1
        if on_quarter_note:
            quarter_note = math.floor(self._pulse_count / 24)
            for observer in self._quarter_note_observers:
                observer(quarter_note)

        on_phrase = self._pulse_count % 384 == 1
        if on_quarter_note:
            phrase = math.floor(self._pulse_count / 384)
            for observer in self._phrase_observers:
                observer()

    def on_quarter_note(self, observer):
        self._quarter_note_observers.append(observer)

    def off_quarter_note(self, observer):
        self._quarter_note_observers.remove(observer)

    def on_phrase(self, observer):
        self._phrase_observers.append(observer)

    def off_phrase(self, observer):
        self._phrase_observers.remove(observer)

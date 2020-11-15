import math

class PulseTracker:
    def __init__(self, divisor=24):
        self._pulse_count = 0
        self._divisor = divisor
        self._observers = []

    def reset_pulse(self):
        self._pulse_count = 0
        self._on_pulse()

    def trigger_pulse(self):
        self._pulse_count += 1
        self._on_pulse()

    def _on_pulse(self):
        on_divisor = self._pulse_count % self._divisor == 0
        if on_divisor:
            count = math.floor(self._pulse_count / self._divisor)
            for observer in self._observers:
                observer(count)

    def on_division(self, observer):
        self._observers.append(observer)

    def off_division(self, observer):
        self._observers.remove(observer)

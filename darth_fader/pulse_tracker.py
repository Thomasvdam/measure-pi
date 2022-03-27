import math

class PulseTracker:
    def __init__(self, divisor=24):
        self._pulse_count = 0
        self._divisor = divisor
        self._observers = []

    def clock_pulse(self):
        self._pulse_count += 1
        self._on_pulse(False)

    def reset(self):
        self._pulse_count = 0
        self._on_pulse(True)

    def _on_pulse(self, reset):
        on_divisor = self._pulse_count % self._divisor == 0
        if on_divisor:
            count = math.floor(self._pulse_count / self._divisor)
            for observer in self._observers:
                observer(count, reset)

    def on_divisor(self, observer):
        self._observers.append(observer)

    def off_divisor(self, observer):
        self._observers.remove(observer)

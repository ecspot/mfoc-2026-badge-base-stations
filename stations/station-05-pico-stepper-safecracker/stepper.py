"""Non-blocking 28BYJ-48/ULN2003 stepper driver."""

from machine import Pin
from time import ticks_diff, ticks_us

HALF_STEP_SEQUENCE = (
    (1, 0, 0, 0),
    (1, 1, 0, 0),
    (0, 1, 0, 0),
    (0, 1, 1, 0),
    (0, 0, 1, 0),
    (0, 0, 1, 1),
    (0, 0, 0, 1),
    (1, 0, 0, 1),
)


class StepperDial:
    def __init__(self, pin_numbers, step_interval_us=1200):
        self._pins = [Pin(number, Pin.OUT) for number in pin_numbers]
        self._step_interval_us = step_interval_us
        self._phase = 0
        self._pending_steps = 0
        self._last_step_us = ticks_us()
        self.release()

    @property
    def is_busy(self):
        return self._pending_steps != 0

    def queue_steps(self, steps):
        self._pending_steps += steps

    def update(self):
        if self._pending_steps == 0:
            return
        now = ticks_us()
        if ticks_diff(now, self._last_step_us) < self._step_interval_us:
            return

        direction = 1 if self._pending_steps > 0 else -1
        self._phase = (self._phase + direction) % len(HALF_STEP_SEQUENCE)
        for pin, level in zip(self._pins, HALF_STEP_SEQUENCE[self._phase]):
            pin.value(level)
        self._pending_steps -= direction
        self._last_step_us = now

    def release(self):
        self._pending_steps = 0
        for pin in self._pins:
            pin.off()

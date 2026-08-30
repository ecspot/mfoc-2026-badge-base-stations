"""NEC receiver/transmitter for the self-contained Pico ultrasonic game."""

from machine import Pin, PWM, disable_irq, enable_irq
from time import sleep_us, ticks_diff, ticks_us

from nec_codec import decode_nec_edges
from station_logic import encode_nec_frame


class NECTransmitter:
    CARRIER_DUTY_U16 = 21845

    def __init__(self, pin_number, carrier_hz=38000):
        self._pwm = PWM(Pin(pin_number, Pin.OUT))
        self._pwm.freq(carrier_hz)
        self.off()

    def _mark(self, duration_us):
        self._pwm.duty_u16(self.CARRIER_DUTY_U16)
        sleep_us(duration_us)
        self.off()

    def send(self, address, command):
        frame = encode_nec_frame(address, command)
        self._mark(9000)
        sleep_us(4500)
        for bit_index in range(32):
            self._mark(560)
            sleep_us(1690 if (frame >> bit_index) & 1 else 560)
        self._mark(560)
        self.off()

    def off(self):
        self._pwm.duty_u16(0)


class NECReceiver:
    MAX_EDGES = 96
    FRAME_IDLE_US = 12000

    def __init__(self, pin_number):
        self._pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)
        self._levels = [0] * self.MAX_EDGES
        self._durations = [0] * self.MAX_EDGES
        self._count = 0
        self._last_edge_us = ticks_us()
        self.resume()

    def _on_edge(self, pin):
        now = ticks_us()
        new_level = pin.value()
        if self._count < self.MAX_EDGES:
            self._levels[self._count] = 0 if new_level else 1
            self._durations[self._count] = ticks_diff(now, self._last_edge_us)
            self._count += 1
        else:
            self._count = 0
        self._last_edge_us = now

    def read(self):
        if self._count < 66 or ticks_diff(ticks_us(), self._last_edge_us) < self.FRAME_IDLE_US:
            return None
        irq_state = disable_irq()
        count = self._count
        levels = self._levels[:count]
        durations = self._durations[:count]
        self._count = 0
        enable_irq(irq_state)
        return decode_nec_edges(levels, durations, count)

    def clear(self):
        irq_state = disable_irq()
        self._count = 0
        self._last_edge_us = ticks_us()
        enable_irq(irq_state)

    def pause(self):
        self._pin.irq(handler=None)
        self.clear()

    def resume(self):
        self.clear()
        self._pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._on_edge)

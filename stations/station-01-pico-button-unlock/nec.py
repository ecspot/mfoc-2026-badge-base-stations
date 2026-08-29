"""Transmit-only extended-NEC driver for Pico Station 1."""

from machine import Pin, PWM
from time import sleep_us

from nec_codec import encode_nec_frame


class NECTransmitter:
    CARRIER_DUTY_U16 = 21845  # Approximately 33%.

    def __init__(self, pin_number, carrier_hz=38000):
        self._pwm = PWM(Pin(pin_number, Pin.OUT))
        self._pwm.freq(carrier_hz)
        self.off()

    def _mark(self, duration_us):
        self._pwm.duty_u16(self.CARRIER_DUTY_U16)
        sleep_us(duration_us)
        self.off()

    @staticmethod
    def _space(duration_us):
        sleep_us(duration_us)

    def _bit(self, value):
        self._mark(560)
        self._space(1690 if value else 560)

    def send(self, address, command):
        """Send one complete extended-NEC frame, least-significant bit first."""
        frame = encode_nec_frame(address, command)
        self._mark(9000)
        self._space(4500)

        for bit_index in range(32):
            self._bit((frame >> bit_index) & 1)

        self._mark(560)
        self.off()

    def off(self):
        self._pwm.duty_u16(0)

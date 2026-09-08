"""NEC transmitter for the Pico IR trigger utility."""

from machine import Pin, PWM
from time import sleep_us

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

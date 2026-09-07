"""MFOC Station 8: receive an NEC IR frame and confirm with an LED."""

from machine import Pin
from time import sleep_ms

from nec import NECReceiver

IR_RECEIVER_PIN = 16
GREEN_LED_PIN = 15
CONFIRMATION_MS = 2000

receiver = NECReceiver(IR_RECEIVER_PIN)
green_led = Pin(GREEN_LED_PIN, Pin.OUT)


def confirm_frame(address, command):
    print(
        "RX NEC address=0x{:04X} command=0x{:02X}".format(
            address,
            command,
        )
    )
    receiver.pause()
    green_led.on()
    sleep_ms(CONFIRMATION_MS)
    green_led.off()
    receiver.resume()
    print("Ready for next IR frame")


def run():
    green_led.off()
    print("MFOC Station 8 - Pico IR confirmation")
    print("IR receiver GP16, green confirmation LED GP15")
    print("Waiting for a valid NEC frame")

    while True:
        frame = receiver.read()
        if frame is not None:
            confirm_frame(*frame)
        sleep_ms(2)


try:
    run()
except KeyboardInterrupt:
    receiver.pause()
    green_led.off()
    print("Station 8 stopped")

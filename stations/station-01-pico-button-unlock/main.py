"""Standalone MFOC Station 1: button-triggered Pico unlock transmitter."""

from machine import Pin
from time import sleep_ms, ticks_diff, ticks_ms

from nec import NECTransmitter
from station_logic import ButtonPressDetector, STATION_ADDRESS, UNLOCK_COMMAND

BUTTON_PIN = 15
IR_TRANSMITTER_PIN = 17
STATUS_LED_PIN = 25

BUTTON_HOLD_MS = 3000
BUTTON_RELEASE_DEBOUNCE_MS = 30
BUTTON_POLL_MS = 5
FULL_FRAME_TRANSMISSIONS = 3
BETWEEN_FRAMES_MS = 120

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
status_led = Pin(STATUS_LED_PIN, Pin.OUT)
transmitter = NECTransmitter(IR_TRANSMITTER_PIN)
press_detector = ButtonPressDetector(
    hold_ms=BUTTON_HOLD_MS,
    release_debounce_ms=BUTTON_RELEASE_DEBOUNCE_MS,
    elapsed_ms=ticks_diff,
)


def send_station_one_unlock():
    print(
        "TX Station 1 unlock address=0x{:04X} command=0x{:02X}".format(
            STATION_ADDRESS,
            UNLOCK_COMMAND,
        )
    )
    status_led.on()
    try:
        for frame_index in range(FULL_FRAME_TRANSMISSIONS):
            transmitter.send(STATION_ADDRESS, UNLOCK_COMMAND)
            if frame_index + 1 < FULL_FRAME_TRANSMISSIONS:
                sleep_ms(BETWEEN_FRAMES_MS)
    finally:
        transmitter.off()
        status_led.off()


def run():
    status_led.off()
    transmitter.off()
    print("MFOC Station 1 - Pico button unlock transmitter")
    print("Button: GP{} to GND".format(BUTTON_PIN))
    print("IR TX: GP{}".format(IR_TRANSMITTER_PIN))
    print("Hold button for 3 seconds to transmit")

    while True:
        is_pressed = button.value() == 0
        if press_detector.update(is_pressed, ticks_ms()):
            send_station_one_unlock()
        sleep_ms(BUTTON_POLL_MS)


try:
    run()
except KeyboardInterrupt:
    transmitter.off()
    status_led.off()
    print("Station 1 stopped")

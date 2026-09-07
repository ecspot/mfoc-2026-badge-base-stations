"""MFOC Station 1: timed button challenge and Pico IR transmitter."""

from machine import Pin
from time import sleep_ms, ticks_diff, ticks_ms

from nec import NECTransmitter
from station_logic import (
    ButtonHoldDetector,
    HOLD_SUCCESS,
    HOLD_TOO_LONG,
    STATION_ADDRESS,
    UNLOCK_COMMAND,
)

BUTTON_PIN = 15
IR_TRANSMITTER_PIN = 17
STATUS_LED_PIN = 25
RED_LED_PIN = 16
GREEN_LED_PIN = 18

BUTTON_HOLD_MS = 3000
BUTTON_MAX_HOLD_MS = 4000
BUTTON_PRESS_DEBOUNCE_MS = 30
BUTTON_RELEASE_DEBOUNCE_MS = 30
BUTTON_POLL_MS = 5
SUCCESS_LED_MS = 3000
FAILURE_LED_MS = 2000
FULL_FRAME_TRANSMISSIONS = 3
BETWEEN_FRAMES_MS = 120

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
status_led = Pin(STATUS_LED_PIN, Pin.OUT)
red_led = Pin(RED_LED_PIN, Pin.OUT)
green_led = Pin(GREEN_LED_PIN, Pin.OUT)
transmitter = NECTransmitter(IR_TRANSMITTER_PIN)
hold_detector = ButtonHoldDetector(
    minimum_hold_ms=BUTTON_HOLD_MS,
    maximum_hold_ms=BUTTON_MAX_HOLD_MS,
    press_debounce_ms=BUTTON_PRESS_DEBOUNCE_MS,
    release_debounce_ms=BUTTON_RELEASE_DEBOUNCE_MS,
    elapsed_ms=ticks_diff,
)


def show_failure(result, held_ms):
    print("FAIL: {} after {} ms".format(result, held_ms))
    red_led.off()
    green_led.off()
    red_led.on()
    sleep_ms(FAILURE_LED_MS)
    red_led.off()


def send_station_one_unlock(held_ms):
    print(
        "SUCCESS: {} ms; TX address=0x{:04X} command=0x{:02X}".format(
            held_ms,
            STATION_ADDRESS,
            UNLOCK_COMMAND,
        )
    )
    red_led.off()
    green_led.on()
    started_ms = ticks_ms()
    try:
        for frame_index in range(FULL_FRAME_TRANSMISSIONS):
            transmitter.send(STATION_ADDRESS, UNLOCK_COMMAND)
            if frame_index + 1 < FULL_FRAME_TRANSMISSIONS:
                sleep_ms(BETWEEN_FRAMES_MS)
        remaining_ms = SUCCESS_LED_MS - ticks_diff(ticks_ms(), started_ms)
        if remaining_ms > 0:
            sleep_ms(remaining_ms)
    finally:
        transmitter.off()
        green_led.off()


def run():
    status_led.off()
    red_led.off()
    green_led.off()
    transmitter.off()
    print("MFOC Station 1 - timed button unlock transmitter")
    print("Button: GP{} to 3.3V".format(BUTTON_PIN))
    print("Red LED: GP{}; green LED: GP{}".format(RED_LED_PIN, GREEN_LED_PIN))
    print("IR TX: GP{}".format(IR_TRANSMITTER_PIN))
    print("Release between 3 and 4 seconds to unlock")

    while True:
        is_pressed = button.value() == 1
        status_led.value(1 if is_pressed else 0)
        result = hold_detector.update(is_pressed, ticks_ms())
        if result is not None:
            outcome, held_ms = result
            status_led.off()
            if outcome == HOLD_SUCCESS:
                send_station_one_unlock(held_ms)
            else:
                if outcome == HOLD_TOO_LONG:
                    print("Release the button before trying again")
                show_failure(outcome, held_ms)

        sleep_ms(BUTTON_POLL_MS)


try:
    run()
except KeyboardInterrupt:
    transmitter.off()
    status_led.off()
    red_led.off()
    green_led.off()
    print("Station 1 button and LED test stopped")

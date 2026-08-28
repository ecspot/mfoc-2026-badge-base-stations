"""MFOC badge base station alpha for Raspberry Pi Pico + MicroPython."""

from machine import Pin
from time import sleep_ms, ticks_add, ticks_diff, ticks_ms

from config import (
    ATTRACTION_PULSE_MS,
    ATTRACTION_TRIGGER_PIN,
    BETWEEN_FRAMES_MS,
    BROADCAST_INTERVAL_MS,
    FULL_FRAME_TRANSMISSIONS,
    IR_RECEIVER_PIN,
    IR_TRANSMITTER_PIN,
    MODE_CONTINUOUS,
    MODE_TRIGGERED,
    RESPONSE_COOLDOWN_MS,
    STATION_MODE,
    STATION_NUMBER,
    STATUS_LED_PIN,
)
from nec import NECReceiver, NECTransmitter
from protocol import UNLOCK_COMMAND, is_badge_trigger_command, make_unlock_address


status_led = Pin(STATUS_LED_PIN, Pin.OUT)
attraction_output = Pin(ATTRACTION_TRIGGER_PIN, Pin.OUT)
receiver = NECReceiver(IR_RECEIVER_PIN)
transmitter = NECTransmitter(IR_TRANSMITTER_PIN)
last_transmission_ms = ticks_add(ticks_ms(), -BROADCAST_INTERVAL_MS)


def pulse_attraction_output():
    attraction_output.on()
    sleep_ms(ATTRACTION_PULSE_MS)
    attraction_output.off()


def send_unlock_frame(reason):
    global last_transmission_ms
    address = make_unlock_address(STATION_NUMBER)
    print(
        "TX unlock address=0x{:04X} command=0x{:02X} reason={}".format(
            address, UNLOCK_COMMAND, reason
        )
    )

    status_led.on()
    receiver.pause()
    try:
        for frame_index in range(FULL_FRAME_TRANSMISSIONS):
            transmitter.send(address, UNLOCK_COMMAND)
            if frame_index + 1 < FULL_FRAME_TRANSMISSIONS:
                sleep_ms(BETWEEN_FRAMES_MS)
    finally:
        transmitter.off()
        receiver.resume()

    pulse_attraction_output()
    status_led.off()
    last_transmission_ms = ticks_ms()


def run():
    if STATION_MODE not in (MODE_TRIGGERED, MODE_CONTINUOUS):
        raise ValueError("STATION_MODE must be 'triggered' or 'continuous'")

    status_led.off()
    attraction_output.off()
    print("MFOC badge base station alpha - Raspberry Pi Pico")
    print(
        "IR RX GP{}, IR TX GP{}, attraction GP{}".format(
            IR_RECEIVER_PIN, IR_TRANSMITTER_PIN, ATTRACTION_TRIGGER_PIN
        )
    )
    print("Mode: {}".format(STATION_MODE))

    while True:
        now = ticks_ms()
        frame = receiver.read()
        if frame is not None:
            address, command = frame
            print("RX NEC address=0x{:04X} command=0x{:02X}".format(address, command))
            ready = ticks_diff(now, last_transmission_ms) >= RESPONSE_COOLDOWN_MS
            if (
                STATION_MODE == MODE_TRIGGERED
                and is_badge_trigger_command(command)
                and ready
            ):
                send_unlock_frame("badge trigger")

        if (
            STATION_MODE == MODE_CONTINUOUS
            and ticks_diff(now, last_transmission_ms) >= BROADCAST_INTERVAL_MS
        ):
            send_unlock_frame("timer")

        sleep_ms(2)


try:
    run()
except KeyboardInterrupt:
    transmitter.off()
    attraction_output.off()
    status_led.off()
    print("Base station stopped")

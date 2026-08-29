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
    RESPONSE_COOLDOWN_MS,
    STATION_ROLE,
    STATION_NUMBER,
    STATUS_LED_PIN,
)
from nec import NECReceiver, NECTransmitter
from protocol import UNLOCK_COMMAND, is_badge_trigger_command, make_unlock_address
from station_roles import (
    ROLE_RECEIVE_ONLY,
    ROLE_TRANSMIT_UNLOCK,
    role_uses_receiver,
    role_uses_transmitter,
    should_transmit_unlock,
    validate_station_role,
)


status_led = Pin(STATUS_LED_PIN, Pin.OUT)
attraction_output = Pin(ATTRACTION_TRIGGER_PIN, Pin.OUT)
validate_station_role(STATION_ROLE)
receiver = NECReceiver(IR_RECEIVER_PIN) if role_uses_receiver(STATION_ROLE) else None
transmitter = (
    NECTransmitter(IR_TRANSMITTER_PIN) if role_uses_transmitter(STATION_ROLE) else None
)
last_transmission_ms = ticks_add(ticks_ms(), -BROADCAST_INTERVAL_MS)


def pulse_attraction_output():
    attraction_output.on()
    sleep_ms(ATTRACTION_PULSE_MS)
    attraction_output.off()


def do_something(address, command):
    """Receive-only extension point for an attraction-specific action."""
    print(
        "TODO do_something address=0x{:04X} command=0x{:02X}".format(
            address, command
        )
    )


def send_unlock_frame(reason):
    global last_transmission_ms
    address = make_unlock_address(STATION_NUMBER)
    print(
        "TX unlock address=0x{:04X} command=0x{:02X} reason={}".format(
            address, UNLOCK_COMMAND, reason
        )
    )

    status_led.on()
    if receiver is not None:
        receiver.pause()
    try:
        for frame_index in range(FULL_FRAME_TRANSMISSIONS):
            transmitter.send(address, UNLOCK_COMMAND)
            if frame_index + 1 < FULL_FRAME_TRANSMISSIONS:
                sleep_ms(BETWEEN_FRAMES_MS)
    finally:
        transmitter.off()
        if receiver is not None:
            receiver.resume()

    pulse_attraction_output()
    status_led.off()
    last_transmission_ms = ticks_ms()


def run():
    status_led.off()
    attraction_output.off()
    print("MFOC badge base station alpha - Raspberry Pi Pico")
    if receiver is not None:
        print("IR RX GP{}".format(IR_RECEIVER_PIN))
    if transmitter is not None:
        print("IR TX GP{}".format(IR_TRANSMITTER_PIN))
    print("Attraction GP{}".format(ATTRACTION_TRIGGER_PIN))
    print("Role: {}".format(STATION_ROLE))

    while True:
        now = ticks_ms()
        frame = receiver.read() if receiver is not None else None
        if frame is not None:
            address, command = frame
            print("RX NEC address=0x{:04X} command=0x{:02X}".format(address, command))
            ready = ticks_diff(now, last_transmission_ms) >= RESPONSE_COOLDOWN_MS
            if STATION_ROLE == ROLE_RECEIVE_ONLY:
                do_something(address, command)
            elif should_transmit_unlock(
                STATION_ROLE,
                is_badge_trigger_command(command),
                ready,
            ):
                send_unlock_frame("badge trigger")

        if (
            STATION_ROLE == ROLE_TRANSMIT_UNLOCK
            and ticks_diff(now, last_transmission_ms) >= BROADCAST_INTERVAL_MS
        ):
            send_unlock_frame("timer")

        sleep_ms(2)


try:
    run()
except KeyboardInterrupt:
    if transmitter is not None:
        transmitter.off()
    attraction_output.off()
    status_led.off()
    print("Base station stopped")

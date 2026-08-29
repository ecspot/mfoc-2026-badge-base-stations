"""MFOC Station 3: receive, reaction-time game, then unlock."""

from machine import Pin
from random import getrandbits
from time import sleep_ms, ticks_add, ticks_diff, ticks_ms

from nec import NECReceiver, NECTransmitter
from station_logic import (
    EVENT_FALSE_START,
    EVENT_GO,
    EVENT_MISSED,
    EVENT_SUCCESS,
    EVENT_TIMEOUT,
    STATE_IDLE,
    STATE_NEEDS_RESTART,
    STATION_ADDRESS,
    UNLOCK_COMMAND,
    ButtonPressDetector,
    ReactionGame,
    is_badge_trigger_command,
    wait_from_random_bits,
)

IR_RECEIVER_PIN = 14
BUTTON_PIN = 15
IR_TRANSMITTER_PIN = 17
STATUS_LED_PIN = 25

FULL_FRAME_TRANSMISSIONS = 3
BETWEEN_FRAMES_MS = 120
LOOP_DELAY_MS = 2

status_led = Pin(STATUS_LED_PIN, Pin.OUT)
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
receiver = NECReceiver(IR_RECEIVER_PIN)
transmitter = NECTransmitter(IR_TRANSMITTER_PIN)
button_detector = ButtonPressDetector(ticks_diff_fn=ticks_diff)
game = ReactionGame(ticks_diff_fn=ticks_diff, ticks_add_fn=ticks_add)


def random_wait_ms():
    return wait_from_random_bits(getrandbits(16))


def send_unlock_frames():
    print(
        "TX Station 3 unlock address=0x{:04X} command=0x{:02X}".format(
            STATION_ADDRESS,
            UNLOCK_COMMAND,
        )
    )
    status_led.on()
    receiver.pause()
    try:
        for frame_index in range(FULL_FRAME_TRANSMISSIONS):
            transmitter.send(STATION_ADDRESS, UNLOCK_COMMAND)
            if frame_index + 1 < FULL_FRAME_TRANSMISSIONS:
                sleep_ms(BETWEEN_FRAMES_MS)
    finally:
        transmitter.off()
        receiver.resume()
    sleep_ms(250)
    status_led.off()


def arm_game(now_ms):
    wait_ms = random_wait_ms()
    game.arm(now_ms=now_ms, wait_ms=wait_ms)
    status_led.off()
    print("ARMED: wait for the LED, then press the button")


def restart_attempt_if_ready(now_ms):
    if game.state != STATE_NEEDS_RESTART:
        return
    if not button_detector.is_released_and_armed:
        return

    wait_ms = random_wait_ms()
    game.restart_attempt(now_ms=now_ms, wait_ms=wait_ms)
    status_led.off()
    print("RETRY: wait for the LED")


def handle_game_event(event):
    if event == EVENT_GO:
        status_led.on()
        print("GO")
    elif event == EVENT_FALSE_START:
        status_led.off()
        print("FALSE START: release the button to retry")
    elif event == EVENT_MISSED:
        status_led.off()
        print("MISSED: starting another attempt")
    elif event == EVENT_SUCCESS:
        print("SUCCESS")
        send_unlock_frames()
        print("Station idle: waiting for badge")
    elif event == EVENT_TIMEOUT:
        status_led.off()
        print("TIMEOUT: waiting for badge")


def poll_badge(now_ms):
    frame = receiver.read()
    if frame is None:
        return

    address, command = frame
    print("RX NEC address=0x{:04X} command=0x{:02X}".format(address, command))
    if is_badge_trigger_command(command):
        if game.state == STATE_IDLE:
            arm_game(now_ms)
        else:
            print("Station already armed; badge trigger ignored")


def run():
    status_led.off()
    print("MFOC Station 3 - Pico reaction-time game")
    print("Locked address=0xFB24 command=0x07")
    print("IR RX GP14, button GP15, IR TX GP17, reaction LED GP25")
    print("Station idle: waiting for badge")

    while True:
        now_ms = ticks_ms()
        poll_badge(now_ms)

        press_event = button_detector.update(
            is_pressed=button.value() == 0,
            now_ms=now_ms,
        )
        event = game.update(now_ms=now_ms, button_pressed=press_event)
        handle_game_event(event)
        restart_attempt_if_ready(now_ms)
        sleep_ms(LOOP_DELAY_MS)


try:
    run()
except KeyboardInterrupt:
    receiver.pause()
    transmitter.off()
    status_led.off()
    print("Station 3 stopped")

"""MFOC Station 3: receive, reaction-time game, then unlock."""

from machine import Pin
from random import getrandbits
from time import sleep_ms, ticks_add, ticks_diff, ticks_ms

from nec import NECReceiver, NECTransmitter
from station_logic import (
    EVENT_FALSE_START,
    EVENT_GO,
    EVENT_MISSED,
    EVENT_ROUND_COMPLETE,
    EVENT_SERIES_FAILED,
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
STATUS_LED_PIN = 13
RED_MISS_LED_PIN = 16
GREEN_SUCCESS_LED_PIN = 17
IR_TRANSMITTER_PIN = 18

BENCH_TEST_MODE = False
LOOP_DELAY_MS = 2
START_BLINK_COUNT = 3
START_BLINK_MS = 200
MISS_LED_MS = 3000
FULL_FRAME_TRANSMISSIONS = 3
BETWEEN_FRAMES_MS = 120

status_led = Pin(STATUS_LED_PIN, Pin.OUT)
red_miss_led = Pin(RED_MISS_LED_PIN, Pin.OUT)
green_success_led = Pin(GREEN_SUCCESS_LED_PIN, Pin.OUT)
button = Pin(BUTTON_PIN, Pin.IN)
receiver = None if BENCH_TEST_MODE else NECReceiver(IR_RECEIVER_PIN)
transmitter = None if BENCH_TEST_MODE else NECTransmitter(IR_TRANSMITTER_PIN)
button_detector = ButtonPressDetector(ticks_diff_fn=ticks_diff)
game = ReactionGame(ticks_diff_fn=ticks_diff, ticks_add_fn=ticks_add)
go_started_ms = None
miss_feedback_until_ms = None


def random_wait_ms():
    return wait_from_random_bits(getrandbits(16))


def blink_start_signal():
    for _ in range(START_BLINK_COUNT):
        status_led.on()
        sleep_ms(START_BLINK_MS)
        status_led.off()
        sleep_ms(START_BLINK_MS)
    status_led.off()


def arm_game():
    global miss_feedback_until_ms

    red_miss_led.off()
    green_success_led.off()
    miss_feedback_until_ms = None
    blink_start_signal()
    wait_ms = random_wait_ms()
    game.arm(now_ms=ticks_ms(), wait_ms=wait_ms)
    status_led.off()
    print("ARMED: wait for the LED, then press the button")


def send_unlock_frames():
    if receiver is None or transmitter is None:
        return
    print(
        "TX Station 3 unlock address=0x{:04X} command=0x{:02X}".format(
            STATION_ADDRESS,
            UNLOCK_COMMAND,
        )
    )
    receiver.pause()
    try:
        for frame_index in range(FULL_FRAME_TRANSMISSIONS):
            transmitter.send(STATION_ADDRESS, UNLOCK_COMMAND)
            if frame_index + 1 < FULL_FRAME_TRANSMISSIONS:
                sleep_ms(BETWEEN_FRAMES_MS)
    finally:
        transmitter.off()
        receiver.resume()


def restart_attempt_if_ready(now_ms):
    if miss_feedback_until_ms is not None:
        return
    if game.state != STATE_NEEDS_RESTART:
        return
    if not button_detector.is_released_and_armed:
        return

    wait_ms = random_wait_ms()
    game.restart_attempt(now_ms=now_ms, wait_ms=wait_ms)
    status_led.off()
    print("RETRY: wait for the LED")


def update_miss_feedback(now_ms):
    global miss_feedback_until_ms

    if miss_feedback_until_ms is None:
        return
    if ticks_diff(now_ms, miss_feedback_until_ms) < 0:
        return

    red_miss_led.off()
    miss_feedback_until_ms = None


def handle_game_event(event, now_ms):
    global go_started_ms, miss_feedback_until_ms

    if event == EVENT_GO:
        go_started_ms = now_ms
        status_led.on()
        print("GO")
    elif event == EVENT_FALSE_START:
        go_started_ms = None
        status_led.off()
        print("FALSE START: release the button to retry")
    elif event == EVENT_MISSED:
        go_started_ms = None
        status_led.off()
        red_miss_led.on()
        miss_feedback_until_ms = ticks_add(now_ms, MISS_LED_MS)
        print("MISSED: red LED on for three seconds")
    elif event == EVENT_ROUND_COMPLETE:
        go_started_ms = None
        status_led.off()
        print(
            "ROUND {}/3: {} ms; total {} ms".format(
                len(game.reaction_times),
                game.last_reaction_ms,
                sum(game.reaction_times),
            )
        )
    elif event == EVENT_SERIES_FAILED:
        go_started_ms = None
        status_led.off()
        red_miss_led.on()
        miss_feedback_until_ms = ticks_add(now_ms, MISS_LED_MS)
        print("SERIES FAILED: total {} ms; must be under 730 ms".format(game.last_total_ms))
    elif event == EVENT_SUCCESS:
        status_led.off()
        green_success_led.on()
        reaction_ms = getattr(game, "last_reaction_ms", None)
        if reaction_ms is None and go_started_ms is not None:
            reaction_ms = ticks_diff(now_ms, go_started_ms)
        print(
            "SUCCESS: third reaction {} ms; three-round total {} ms".format(
                reaction_ms,
                game.last_total_ms,
            )
        )
        go_started_ms = None
        if BENCH_TEST_MODE:
            print("BENCH TEST: IR unlock transmission disabled")
            print("Station idle: reset to play again")
        else:
            send_unlock_frames()
            print("Station idle: waiting for badge")
    elif event == EVENT_TIMEOUT:
        go_started_ms = None
        status_led.off()
        red_miss_led.off()
        green_success_led.off()
        print("TIMEOUT: waiting for badge")


def poll_badge():
    if receiver is None:
        return
    frame = receiver.read()
    if frame is None:
        return

    address, command = frame
    print("RX NEC address=0x{:04X} command=0x{:02X}".format(address, command))
    if is_badge_trigger_command(command):
        if game.state == STATE_IDLE:
            arm_game()
        else:
            print("Station already armed; badge trigger ignored")


def run():
    status_led.off()
    red_miss_led.off()
    green_success_led.off()
    print("MFOC Station 3 - Pico reaction-time game")
    print("IR RX GP14, reaction GP13, button GP15, miss GP16, success GP17, IR TX GP18")
    if BENCH_TEST_MODE:
        print("BENCH TEST: IR disabled; starting automatically")
        arm_game()
    else:
        print("Station idle: waiting for badge")

    while True:
        now_ms = ticks_ms()
        if not BENCH_TEST_MODE:
            poll_badge()

        press_event = button_detector.update(
            is_pressed=button.value() == 1,
            now_ms=now_ms,
        )
        event = game.update(now_ms=now_ms, button_pressed=press_event)
        handle_game_event(event, now_ms)
        update_miss_feedback(now_ms)
        restart_attempt_if_ready(now_ms)
        sleep_ms(LOOP_DELAY_MS)


try:
    run()
except KeyboardInterrupt:
    if receiver is not None:
        receiver.pause()
    if transmitter is not None:
        transmitter.off()
    status_led.off()
    red_miss_led.off()
    green_success_led.off()
    print("Station 3 stopped")

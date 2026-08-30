"""MFOC Station 5: Pico stepper safecracker."""

from machine import Pin
from random import getrandbits
from time import sleep_ms, ticks_add, ticks_diff, ticks_ms

from nec import NECReceiver, NECTransmitter
from station_logic import (
    EVENT_CODE_CORRECT,
    EVENT_CODE_WRONG,
    EVENT_GAME_COMPLETE,
    STATION_ADDRESS,
    UNLOCK_COMMAND,
    ButtonPressDetector,
    SafecrackerGame,
    code_from_random_values,
    game_timed_out,
    is_badge_trigger_command,
    next_digit,
    previous_digit,
    segments_for_digit,
    step_delta_for_digit_change,
)
from stepper import StepperDial

SEGMENT_PINS = (0, 1, 2, 3, 4, 5, 6)
RED_LED_PIN = 7
GREEN_LED_PIN = 8
UP_BUTTON_PIN = 10
DOWN_BUTTON_PIN = 11
SELECT_BUTTON_PIN = 12
IR_RECEIVER_PIN = 14
IR_TRANSMITTER_PIN = 17
STEPPER_PINS = (18, 19, 20, 21)

PRESENT_DIGIT_MS = 700
PRESENT_BLANK_MS = 250
FEEDBACK_MS = 900
FULL_FRAME_TRANSMISSIONS = 3
BETWEEN_FRAMES_MS = 120

STATE_IDLE = "idle"
STATE_PRESENTING = "presenting"
STATE_ENTERING = "entering"
STATE_FEEDBACK = "feedback"

segment_outputs = [Pin(pin, Pin.OUT) for pin in SEGMENT_PINS]
red_led = Pin(RED_LED_PIN, Pin.OUT)
green_led = Pin(GREEN_LED_PIN, Pin.OUT)
up_button = Pin(UP_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
down_button = Pin(DOWN_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
select_button = Pin(SELECT_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
receiver = NECReceiver(IR_RECEIVER_PIN)
transmitter = NECTransmitter(IR_TRANSMITTER_PIN)
stepper = StepperDial(STEPPER_PINS)

up_detector = ButtonPressDetector(ticks_diff_fn=ticks_diff)
down_detector = ButtonPressDetector(ticks_diff_fn=ticks_diff)
select_detector = ButtonPressDetector(ticks_diff_fn=ticks_diff)
game = SafecrackerGame()

state = STATE_IDLE
game_started_ms = 0
current_code = ()
presentation_index = 0
presentation_showing = False
state_deadline_ms = 0
selected_digit = 0
feedback_event = None


def display_digit(digit):
    for pin, level in zip(segment_outputs, segments_for_digit(digit)):
        pin.value(level)


def blank_display():
    for pin in segment_outputs:
        pin.off()


def set_feedback(red=False, green=False):
    red_led.value(1 if red else 0)
    green_led.value(1 if green else 0)


def random_code():
    return code_from_random_values([getrandbits(16) for _ in range(6)])


def move_dial_to(target_digit):
    global selected_digit
    while selected_digit != target_digit:
        clockwise_distance = (target_digit - selected_digit) % 10
        direction = 1 if clockwise_distance <= 5 else -1
        stepper.queue_steps(
            step_delta_for_digit_change(selected_digit, direction)
        )
        selected_digit = (
            next_digit(selected_digit)
            if direction == 1
            else previous_digit(selected_digit)
        )


def begin_code(now_ms):
    global current_code, presentation_index, presentation_showing
    global state, state_deadline_ms

    current_code = random_code()
    game.begin_code(current_code)
    state = STATE_PRESENTING
    presentation_index = 0
    presentation_showing = True
    set_feedback()
    display_digit(current_code[0])
    state_deadline_ms = ticks_add(now_ms, PRESENT_DIGIT_MS)
    print(
        "CODE {}/3 length={}: {}".format(
            game.correct_codes + 1,
            len(current_code),
            "".join(str(digit) for digit in current_code),
        )
    )


def begin_entry():
    global state
    move_dial_to(0)
    display_digit(selected_digit)
    state = STATE_ENTERING
    print("ENTER: use Up/Down, then Select for each digit")


def update_presentation(now_ms):
    global presentation_index, presentation_showing, state_deadline_ms
    if ticks_diff(now_ms, state_deadline_ms) < 0:
        return

    if presentation_showing:
        blank_display()
        presentation_showing = False
        state_deadline_ms = ticks_add(now_ms, PRESENT_BLANK_MS)
        return

    presentation_index += 1
    if presentation_index >= len(current_code):
        begin_entry()
        return

    display_digit(current_code[presentation_index])
    presentation_showing = True
    state_deadline_ms = ticks_add(now_ms, PRESENT_DIGIT_MS)


def begin_feedback(event, now_ms):
    global state, state_deadline_ms, feedback_event
    state = STATE_FEEDBACK
    feedback_event = event
    blank_display()
    set_feedback(
        red=event == EVENT_CODE_WRONG,
        green=event == EVENT_CODE_CORRECT,
    )
    state_deadline_ms = ticks_add(now_ms, FEEDBACK_MS)


def update_feedback(now_ms):
    if ticks_diff(now_ms, state_deadline_ms) < 0:
        return
    begin_code(now_ms)


def send_unlock_frames():
    print(
        "TX safecracker unlock address=0x{:04X} command=0x{:02X}".format(
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


def finish_game(reason):
    global state
    state = STATE_IDLE
    blank_display()
    stepper.release()
    print("Station idle: {}".format(reason))


def complete_game():
    set_feedback(green=True)
    display_digit(3)
    print("SUCCESS: three correct codes")
    send_unlock_frames()
    sleep_ms(1000)
    set_feedback()
    finish_game("waiting for badge")


def handle_entry(now_ms):
    global selected_digit
    up_event = up_detector.update(up_button.value() == 0, now_ms)
    down_event = down_detector.update(down_button.value() == 0, now_ms)
    select_event = select_detector.update(select_button.value() == 0, now_ms)

    if stepper.is_busy:
        return

    if up_event:
        stepper.queue_steps(step_delta_for_digit_change(selected_digit, 1))
        selected_digit = next_digit(selected_digit)
        display_digit(selected_digit)
    elif down_event:
        stepper.queue_steps(step_delta_for_digit_change(selected_digit, -1))
        selected_digit = previous_digit(selected_digit)
        display_digit(selected_digit)
    elif select_event:
        result = game.select_digit(selected_digit)
        print("Selected {}".format(selected_digit))
        if result == EVENT_GAME_COMPLETE:
            complete_game()
        elif result in (EVENT_CODE_CORRECT, EVENT_CODE_WRONG):
            print(
                "CORRECT ({}/3)".format(game.correct_codes)
                if result == EVENT_CODE_CORRECT
                else "WRONG: generating a new code"
            )
            begin_feedback(result, now_ms)


def update_button_detectors(now_ms):
    if state == STATE_ENTERING:
        handle_entry(now_ms)
        return
    up_detector.update(up_button.value() == 0, now_ms)
    down_detector.update(down_button.value() == 0, now_ms)
    select_detector.update(select_button.value() == 0, now_ms)


def arm_game(now_ms):
    global game_started_ms
    game.reset()
    game_started_ms = now_ms
    move_dial_to(0)
    begin_code(now_ms)
    print("ARMED: memorize and enter three codes")


def poll_badge(now_ms):
    frame = receiver.read()
    if frame is None:
        return
    address, command = frame
    print("RX NEC address=0x{:04X} command=0x{:02X}".format(address, command))
    if is_badge_trigger_command(command):
        if state == STATE_IDLE:
            arm_game(now_ms)
        else:
            print("Game already active; badge trigger ignored")


def run():
    blank_display()
    set_feedback()
    print("MFOC Station 5 - Pico stepper safecracker")
    print("Locked address=0xFB30 command=0x07")
    print("Station idle: waiting for badge")

    while True:
        now_ms = ticks_ms()
        stepper.update()
        poll_badge(now_ms)

        if state != STATE_IDLE and game_timed_out(
            now_ms,
            game_started_ms,
            ticks_diff_fn=ticks_diff,
        ):
            set_feedback(red=True)
            sleep_ms(300)
            set_feedback()
            finish_game("two-minute timeout")
        else:
            update_button_detectors(now_ms)
            if state == STATE_PRESENTING:
                update_presentation(now_ms)
            elif state == STATE_FEEDBACK:
                update_feedback(now_ms)

        sleep_ms(1)


try:
    run()
except KeyboardInterrupt:
    receiver.pause()
    transmitter.off()
    stepper.release()
    blank_display()
    set_feedback()
    print("Safecracker stopped")

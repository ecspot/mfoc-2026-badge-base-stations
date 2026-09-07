"""MFOC Station 7: Pico Simon memory game."""

from machine import Pin, PWM
from random import getrandbits
from time import sleep_ms, ticks_add, ticks_diff, ticks_ms

from nec import NECReceiver, NECTransmitter
from station_logic import (
    EVENT_GAME_COMPLETE,
    EVENT_ROUND_COMPLETE,
    EVENT_WRONG,
    STATION_ADDRESS,
    UNLOCK_COMMAND,
    ButtonPressDetector,
    SimonGame,
    game_timed_out,
    is_badge_trigger_command,
    sequence_from_random_values,
)

LED_PINS = (2, 3, 4, 5)
BUTTON_PINS = (6, 7, 8, 9)
BUZZER_PIN = 10
IR_RECEIVER_PIN = 14
IR_TRANSMITTER_PIN = 17

TONE_FREQUENCIES = (262, 330, 392, 523)
SHOW_ON_MS = 400
SHOW_OFF_MS = 180
FULL_FRAME_TRANSMISSIONS = 3
BETWEEN_FRAMES_MS = 120

STATE_IDLE = "idle"
STATE_SHOW_ON = "show_on"
STATE_SHOW_OFF = "show_off"
STATE_INPUT = "input"

leds = [Pin(pin, Pin.OUT) for pin in LED_PINS]
buttons = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in BUTTON_PINS]
detectors = [ButtonPressDetector(ticks_diff_fn=ticks_diff) for _ in BUTTON_PINS]
buzzer = PWM(Pin(BUZZER_PIN, Pin.OUT))
buzzer.duty_u16(0)
receiver = NECReceiver(IR_RECEIVER_PIN)
transmitter = NECTransmitter(IR_TRANSMITTER_PIN)

state = STATE_IDLE
game = None
game_started_ms = 0
show_index = 0
state_deadline_ms = 0


def all_outputs_off():
    for led in leds:
        led.off()
    buzzer.duty_u16(0)


def light_color(color):
    all_outputs_off()
    leds[color].on()
    buzzer.freq(TONE_FREQUENCIES[color])
    buzzer.duty_u16(16000)


def random_sequence():
    return sequence_from_random_values(tuple(getrandbits(16) for _ in range(6)))


def start_round(now_ms):
    global state, show_index, state_deadline_ms
    show_index = 0
    light_color(game.sequence[0])
    state = STATE_SHOW_ON
    state_deadline_ms = ticks_add(now_ms, SHOW_ON_MS)
    print("ROUND length={}".format(game.round_length))


def begin_new_game(now_ms):
    global game, game_started_ms
    game = SimonGame(random_sequence())
    game_started_ms = now_ms
    print("NEW GAME")
    start_round(now_ms)


def update_show(now_ms):
    global state, show_index, state_deadline_ms
    if ticks_diff(now_ms, state_deadline_ms) < 0:
        return

    if state == STATE_SHOW_ON:
        all_outputs_off()
        state = STATE_SHOW_OFF
        state_deadline_ms = ticks_add(now_ms, SHOW_OFF_MS)
        return

    show_index += 1
    if show_index >= game.round_length:
        state = STATE_INPUT
        all_outputs_off()
        print("REPEAT")
        return

    light_color(game.sequence[show_index])
    state = STATE_SHOW_ON
    state_deadline_ms = ticks_add(now_ms, SHOW_ON_MS)


def flash_all(times, frequency=196):
    for _ in range(times):
        for led in leds:
            led.on()
        buzzer.freq(frequency)
        buzzer.duty_u16(16000)
        sleep_ms(140)
        all_outputs_off()
        sleep_ms(100)


def send_unlock_frames():
    print(
        "TX Simon unlock address=0x{:04X} command=0x{:02X}".format(
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
    global state, game
    state = STATE_IDLE
    game = None
    all_outputs_off()
    print("Station idle: {}".format(reason))


def handle_color_press(color, now_ms):
    light_color(color)
    sleep_ms(140)
    all_outputs_off()

    result = game.press(color)
    if result == EVENT_WRONG:
        print("WRONG: generating a fresh game")
        flash_all(2, frequency=110)
        begin_new_game(ticks_ms())
    elif result == EVENT_ROUND_COMPLETE:
        print("ROUND COMPLETE")
        flash_all(1, frequency=660)
        start_round(ticks_ms())
    elif result == EVENT_GAME_COMPLETE:
        print("SUCCESS: all four rounds complete")
        flash_all(3, frequency=880)
        send_unlock_frames()
        finish_game("waiting for badge")


def update_buttons(now_ms):
    pressed_color = None
    for color, (button, detector) in enumerate(zip(buttons, detectors)):
        if detector.update(button.value() == 0, now_ms) and pressed_color is None:
            pressed_color = color
    if state == STATE_INPUT and pressed_color is not None:
        handle_color_press(pressed_color, now_ms)


def poll_badge(now_ms):
    frame = receiver.read()
    if frame is None:
        return
    address, command = frame
    print("RX NEC address=0x{:04X} command=0x{:02X}".format(address, command))
    if is_badge_trigger_command(command):
        if state == STATE_IDLE:
            begin_new_game(now_ms)
            print("ARMED: watch and repeat the lights")
        else:
            print("Game already active; badge trigger ignored")


def run():
    all_outputs_off()
    print("MFOC Station 7 - Pico Simon memory")
    print(
        "Locked address=0x{:04X} command=0x{:02X}".format(
            STATION_ADDRESS,
            UNLOCK_COMMAND,
        )
    )
    print("Station idle: waiting for badge")

    while True:
        now_ms = ticks_ms()
        poll_badge(now_ms)

        if state != STATE_IDLE and game_timed_out(
            now_ms,
            game_started_ms,
            ticks_diff_fn=ticks_diff,
        ):
            flash_all(1, frequency=110)
            finish_game("60-second timeout")
        else:
            update_buttons(now_ms)
            if state in (STATE_SHOW_ON, STATE_SHOW_OFF):
                update_show(now_ms)

        sleep_ms(2)


try:
    run()
except KeyboardInterrupt:
    receiver.pause()
    transmitter.off()
    all_outputs_off()
    buzzer.deinit()
    print("Simon game stopped")

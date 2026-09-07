"""MFOC Station 6: Pico ultrasonic distance code."""

from machine import Pin, time_pulse_us
from random import getrandbits
from time import sleep_ms, sleep_us, ticks_add, ticks_diff, ticks_ms

from nec import NECReceiver, NECTransmitter
from station_logic import (
    EVENT_GAME_COMPLETE,
    EVENT_STEP_COMPLETE,
    MAX_TARGETS,
    STATION_ADDRESS,
    UNLOCK_COMMAND,
    DistanceGame,
    ZONE_FAR,
    ZONE_MIDDLE,
    ZONE_NEAR,
    classify_distance_cm,
    is_badge_trigger_command,
    sequence_from_random_values,
)

TRIGGER_PIN = 2
ECHO_PIN = 15
NEAR_LED_PIN = 6
MIDDLE_LED_PIN = 7
FAR_LED_PIN = 8
IR_RECEIVER_PIN = 14
IR_TRANSMITTER_PIN = 17
SUCCESS_LED_PIN = 18

SAMPLE_INTERVAL_MS = 60
GAME_TIMEOUT_MS = 45000
SUCCESS_LED_MS = 3000
FULL_FRAME_TRANSMISSIONS = 3
BETWEEN_FRAMES_MS = 120

trigger = Pin(TRIGGER_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)
zone_leds = {
    ZONE_NEAR: Pin(NEAR_LED_PIN, Pin.OUT),
    ZONE_MIDDLE: Pin(MIDDLE_LED_PIN, Pin.OUT),
    ZONE_FAR: Pin(FAR_LED_PIN, Pin.OUT),
}
receiver = NECReceiver(IR_RECEIVER_PIN)
transmitter = NECTransmitter(IR_TRANSMITTER_PIN)
success_led = Pin(SUCCESS_LED_PIN, Pin.OUT)

active = False
game = None
game_started_ms = 0
next_sample_ms = 0


def all_leds_off():
    for led in zone_leds.values():
        led.off()


def all_zone_leds_on():
    for led in zone_leds.values():
        led.on()


def flash_zone_leds(count, on_ms, off_ms):
    for _ in range(count):
        all_zone_leds_on()
        sleep_ms(on_ms)
        all_leds_off()
        sleep_ms(off_ms)


def show_target(zone):
    all_leds_off()
    zone_leds[zone].on()
    print("TARGET {}".format(zone.upper()))


def read_distance_cm():
    trigger.off()
    sleep_us(2)
    trigger.on()
    sleep_us(10)
    trigger.off()
    try:
        pulse_us = time_pulse_us(echo, 1, 30000)
    except OSError:
        return None
    if pulse_us < 0:
        return None
    return pulse_us / 58.0


def send_unlock_frames():
    print(
        "TX ultrasonic unlock address=0x{:04X} command=0x{:02X}".format(
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
    global active, game
    active = False
    game = None
    all_leds_off()
    success_led.off()
    print("Station idle: {}".format(reason))


def complete_game():
    print("SUCCESS: {} distance targets completed".format(len(game.sequence)))
    flash_zone_leds(3, 120, 100)
    success_led.on()
    send_unlock_frames()
    sleep_ms(SUCCESS_LED_MS)
    success_led.off()
    finish_game("waiting for badge")


def shutdown_game(reason):
    print("SHUTDOWN: {}".format(reason))
    success_led.off()
    flash_zone_leds(4, 250, 250)
    finish_game("{}; reset to play again".format(reason))


def arm_game(now_ms):
    global active, game, game_started_ms, next_sample_ms
    sequence = sequence_from_random_values(
        [getrandbits(16) for _ in range(MAX_TARGETS + 1)]
    )
    game = DistanceGame(sequence, ticks_diff_fn=ticks_diff)
    active = True
    game_started_ms = now_ms
    next_sample_ms = now_ms
    print("ARMED sequence={}".format(" -> ".join(sequence)))
    show_target(game.expected_zone)


def update_game(now_ms):
    global next_sample_ms
    if ticks_diff(now_ms, next_sample_ms) < 0:
        return
    next_sample_ms = ticks_add(now_ms, SAMPLE_INTERVAL_MS)

    distance_cm = read_distance_cm()
    measured_zone = (
        classify_distance_cm(distance_cm)
        if distance_cm is not None
        else None
    )
    result = game.update(measured_zone, now_ms)
    if result == EVENT_STEP_COMPLETE:
        print("STEP COMPLETE {}/{}".format(game.step_index, len(game.sequence)))
        all_leds_off()
        sleep_ms(150)
        show_target(game.expected_zone)
    elif result == EVENT_GAME_COMPLETE:
        complete_game()


def poll_badge(now_ms):
    frame = receiver.read()
    if frame is None:
        return
    address, command = frame
    print("RX NEC address=0x{:04X} command=0x{:02X}".format(address, command))
    if is_badge_trigger_command(command):
        if not active:
            arm_game(now_ms)
        else:
            print("Game already active; badge trigger ignored")


def run():
    trigger.off()
    all_leds_off()
    success_led.off()
    print("MFOC Station 6 - Pico ultrasonic distance code")
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
        if active:
            if ticks_diff(now_ms, game_started_ms) >= GAME_TIMEOUT_MS:
                shutdown_game("45-second timeout")
            else:
                update_game(now_ms)
        sleep_ms(2)


try:
    run()
except KeyboardInterrupt:
    receiver.pause()
    transmitter.off()
    all_leds_off()
    success_led.off()
    print("Ultrasonic game stopped")

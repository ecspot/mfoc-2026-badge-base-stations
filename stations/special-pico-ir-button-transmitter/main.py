"""Button-operated NEC 0x01 transmitter for Raspberry Pi Pico."""

from machine import Pin
from time import sleep_ms, ticks_diff, ticks_ms

from nec import NECTransmitter
from station_logic import (
    NEC_ADDRESS,
    TRIGGER_COMMAND,
    ButtonPressDetector,
)

BUTTON_PIN = 16
IR_TRANSMITTER_PIN = 15
FULL_FRAME_TRANSMISSIONS = 3
BETWEEN_FRAMES_MS = 120
LOOP_DELAY_MS = 2

button = Pin(BUTTON_PIN, Pin.IN)
transmitter = NECTransmitter(IR_TRANSMITTER_PIN)
button_detector = ButtonPressDetector(ticks_diff_fn=ticks_diff)


def send_trigger_frames():
    print(
        "TX NEC address=0x{:04X} command=0x{:02X}".format(
            NEC_ADDRESS,
            TRIGGER_COMMAND,
        )
    )
    try:
        for frame_index in range(FULL_FRAME_TRANSMISSIONS):
            transmitter.send(NEC_ADDRESS, TRIGGER_COMMAND)
            if frame_index + 1 < FULL_FRAME_TRANSMISSIONS:
                sleep_ms(BETWEEN_FRAMES_MS)
    finally:
        transmitter.off()


def run():
    transmitter.off()
    print("MFOC Pico IR station trigger")
    print("Button GP16 / physical pin 21")
    print("IR transmitter GP15 / physical pin 20")
    print("Press button to send NEC command 0x01")

    while True:
        now_ms = ticks_ms()
        if button_detector.update(button.value() == 1, now_ms):
            send_trigger_frames()
        sleep_ms(LOOP_DELAY_MS)


try:
    run()
except KeyboardInterrupt:
    transmitter.off()
    print("IR trigger stopped")

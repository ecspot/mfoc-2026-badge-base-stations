"""Editable Raspberry Pi Pico base-station configuration."""

# Pico GPIO wiring defaults (physical pin numbers in comments):
IR_RECEIVER_PIN = 16       # GP16, physical pin 21; receiver OUT
IR_TRANSMITTER_PIN = 17    # GP17, physical pin 22; transistor input
ATTRACTION_TRIGGER_PIN = 18  # GP18, physical pin 24; logic pulse output
STATUS_LED_PIN = "LED"

STATION_NUMBER = 1  # Valid values: 1..5

MODE_TRIGGERED = "triggered"
MODE_CONTINUOUS = "continuous"
STATION_MODE = MODE_TRIGGERED

BROADCAST_INTERVAL_MS = 2000
RESPONSE_COOLDOWN_MS = 750
ATTRACTION_PULSE_MS = 250
FULL_FRAME_TRANSMISSIONS = 3
BETWEEN_FRAMES_MS = 120

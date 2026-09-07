# Station 5 — Pico Stepper Safecracker

Self-contained Raspberry Pi Pico / MicroPython receive–interact–transmit game.

## Identity

- Address: **`0xFB30`**.
- Unlock command: **`0x07`**.
- Extended-NEC frame: **`0xF807FB30`**.

## Game

1. A badge advertisement (`0x01`) or report (`0x20`–`0x2F`) arms the game.
2. The common-cathode display presents a random 3–5 digit code one digit at a
   time.
3. The display switches to entry mode.
4. Up and Down change the digit and move the stepper-driven physical dial.
5. Select commits the displayed digit.
6. A wrong code flashes red and generates a new code. Previously completed
   correct codes remain counted.
7. A correct code flashes green. Three correct codes transmit three full Station
   5 unlock frames.

The game times out after two minutes without transmitting.

## Wiring

| Function | Pico GPIO |
|---|---:|
| Seven-segment A–G | GP0–GP6 |
| Red failure LED | GP7 |
| Green success LED | GP8 |
| Up button to GND | GP10 |
| Down button to GND | GP11 |
| Select button to GND | GP12 |
| TSOP98638 output | GP14 |
| LTE-4208 driver control | GP17 |
| ULN2003 IN1–IN4 | GP18–GP21 |

Use a **common-cathode** one-digit display. Connect its common cathode pin(s) to
GND and place a separate 220–330 Ω resistor in series with every segment. The
red and green LEDs also require individual resistors. Buttons use Pico internal
pull-ups.

### Stepper

Use a 28BYJ-48 with its ULN2003 board. Power the motor/driver from a regulated
5 V supply, not from Pico 3.3 V, and connect the supply ground to Pico GND.
Before powering the station, attach or align the physical pointer at digit 0.
Ten digit increments are distributed across a nominal 4,096 half-step output
revolution. Actual 28BYJ-48 gearbox ratios vary; calibrate
`STEPPER_DIGIT_BOUNDARIES` if the pointer does not return exactly to 0 after ten
increments.

### IR

Power the TSOP98638 from 3.3 V. Drive the LTE-4208 through a current-limited
transistor/MOSFET stage; never directly at useful pulse current from GP17.

## Load

Copy these files to the Pico root using Thonny or `mpremote`:

- `main.py`
- `station_logic.py`
- `stepper.py`
- `nec.py`
- `nec_codec.py`

Reset the Pico. Serial output identifies code presentation, selected digits,
correct progress, failures, and transmission. The generated code is also printed
to serial to simplify tomorrow’s bench testing.

## Tests

From this directory:

```bash
python -m unittest discover -s tests -v
```

Bench-test a wrong code, then three correct codes. Confirm the wrong code does
not clear prior correct progress and that no unlock is sent before the third
correct code.

# Station 7 — Pico Simon Memory

Self-contained Raspberry Pi Pico / MicroPython receive–interact–transmit game.

## Identity

- Address: **`0xFB80`**.
- Unlock command: **`0x07`**.
- Extended-NEC frame: **`0xF807FB80`**.

This is an independent Station 7 deployment. The badge firmware flashed for the
event must include the registered Station 7 achievement address; badge firmware
is not modified by this repository.

## Game

1. A recognized badge frame generates a random six-step sequence using four colors.
2. The station presents rounds of 3, 4, 5, and 6 lights.
3. The player repeats each round with the four matching buttons.
4. A wrong button flashes all lights with a low error tone and generates a new
   sequence from round one without transmitting.
5. Completing all four rounds flashes success and sends three full Station 7
   unlock frames.

The game times out after 60 seconds without transmitting. Buttons use 30 ms
debounce and report once until released.

## Wiring

Arrange each button beside its corresponding LED.

| Position/color | LED GPIO | Button GPIO |
|---|---:|---:|
| 1 | GP2 | GP6 |
| 2 | GP3 | GP7 |
| 3 | GP4 | GP8 |
| 4 | GP5 | GP9 |

Additional connections:

| Function | Pico GPIO |
|---|---:|
| Passive piezo buzzer | GP10 |
| TSOP98638 output | GP14 |
| LTE-4208 driver control | GP17 |

Buttons connect between GPIO and GND and use internal pull-ups. Each LED needs a
220–330 Ω series resistor. A small passive piezo element can be driven from GP10;
use a transistor if the selected buzzer requires more current than a GPIO can
safely provide.

Power the TSOP98638 from 3.3 V. Drive the LTE-4208 through a current-limited
transistor/MOSFET stage.

## Load

Copy to the Pico root:

- `main.py`
- `station_logic.py`
- `nec.py`
- `nec_codec.py`

Reset and monitor serial output for round lengths, wrong attempts, success, and
transmission.

## Tests

```bash
python -m unittest discover -s tests -v
```

Bench-test all four buttons and tones, a wrong first input, all four correct
rounds, timeout behavior, and absence of startup/idle transmission.

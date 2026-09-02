# Station 6 — Pico Ultrasonic Distance Code

Self-contained Raspberry Pi Pico / MicroPython distance game. This temporary
bench-test build starts automatically and does not initialize IR reception or
transmission.

## Identity

- Address: **`0xFB40`**.
- Unlock command: **`0x07`**.
- Extended-NEC frame: **`0xF807FB40`**.

This is an independent Station 6 deployment. The badge firmware flashed for the
event must include the registered Station 6 achievement address; badge firmware
is not modified by this repository.

## Game

1. Resetting the Pico arms a 45-second game automatically without a badge.
2. The station randomly chooses **4–7** near/middle/far targets with no adjacent
   repeat.
3. The matching LED identifies the requested zone.
4. The player holds a hand continuously in the zone for 750 ms.
5. Leaving the zone or entering a safety gap resets only the current hold.
6. Completing all targets turns on the green GP18 success LED for three
   seconds to simulate sending the Station 6 unlock frames.

If the 45-second game timer expires, all three zone LEDs flash together four
times at a slower rate, then the station turns every LED off. Green GP18 is used
only for success and will remain part of the final IR-enabled build.

Distance zones:

| Zone | Range |
|---|---:|
| Near | 8–14 cm |
| Middle | 18–26 cm |
| Far | 32–45 cm |

## Wiring

| Function | Pico GPIO |
|---|---:|
| HC-SR04 Trigger | GP2 |
| HC-SR04 divided Echo | GP15 |
| Near LED | GP6 |
| Middle LED | GP7 |
| Far LED | GP8 |
| TSOP98638 output | GP14 |
| LTE-4208 driver control | GP17 |
| Green simulated-unlock LED | GP18 |

Each visible LED, including the green GP18 success LED, requires its own 220–330
Ω series resistor.

### HC-SR04 Echo protection

HC-SR04 Echo is nominally 5 V and must not connect directly to Pico GPIO. Use a
resistor divider:

```text
HC-SR04 Echo -- 1 kΩ --+-- GP15
                       |
                      2 kΩ
                       |
                      GND
```

Power the HC-SR04 from 5 V and share ground with the Pico. GP2 provides the
trigger signal. Verify that the specific sensor recognizes the Pico’s 3.3 V
trigger-high level.

### IR

The bench-test build does not initialize GP14 or GP17, so neither IR component is
needed while testing the ultrasonic game. On success, GP18 lights for three
seconds in place of an unlock transmission.

## Load

Copy to the Pico root:

- `main.py`
- `station_logic.py`

Reset and monitor serial output. The game starts automatically and prints the
generated target sequence and accepted steps.

## Tests

```bash
python -m unittest discover -s tests -v
```

Confirm that readings in the gaps do not advance the game, every zone requires
a complete 750 ms hold, each game contains 4–7 targets, timeout produces four
shutdown flashes while leaving GP18 off, and success lights GP18 for three
seconds without transmitting IR. Reset the Pico to start another game.

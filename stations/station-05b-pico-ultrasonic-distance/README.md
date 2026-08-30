# Station 5B — Pico Ultrasonic Distance Code

Self-contained Raspberry Pi Pico / MicroPython receive–interact–transmit game.
It is an alternative Station 5 deployment.

## Identity and badge limitation

- Address: **`0xFB30`**.
- Unlock command: **`0x07`**.
- Extended-NEC frame: **`0xF807FB30`**.

Station 5A, 5B, and 5C share achievement 5 because the badge exposes only five
one-hot achievement bits.

## Game

1. A recognized badge frame arms a 45-second game.
2. The station generates three near/middle/far targets with no adjacent repeat.
3. The matching LED identifies the requested zone.
4. The player holds a hand continuously in the zone for 750 ms.
5. Leaving the zone or entering a safety gap resets only the current hold.
6. Completing all three targets sends three full Station 5 unlock frames.

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
| HC-SR04 divided Echo | GP3 |
| Near LED | GP6 |
| Middle LED | GP7 |
| Far LED | GP8 |
| TSOP98638 output | GP14 |
| LTE-4208 driver control | GP17 |

Each visible LED requires a 220–330 Ω series resistor.

### HC-SR04 Echo protection

HC-SR04 Echo is nominally 5 V and must not connect directly to Pico GPIO. Use a
resistor divider:

```text
HC-SR04 Echo -- 1 kΩ --+-- GP3
                       |
                      2 kΩ
                       |
                      GND
```

Power the HC-SR04 from 5 V and share ground with the Pico. GP2 provides the
trigger signal. Verify that the specific sensor recognizes the Pico’s 3.3 V
trigger-high level.

### IR

Power the TSOP98638 from 3.3 V. Use a transistor/MOSFET and current-limiting
resistor for the LTE-4208 emitter on GP17.

## Load

Copy to the Pico root:

- `main.py`
- `station_logic.py`
- `nec.py`
- `nec_codec.py`

Reset and monitor serial output. It prints the generated target sequence and
accepted steps for straightforward bench testing.

## Tests

```bash
python -m unittest discover -s tests -v
```

Confirm that readings in the gaps do not advance the game, every zone requires
a complete 750 ms hold, timeout sends nothing, and success sends exactly three
complete unlock frames.

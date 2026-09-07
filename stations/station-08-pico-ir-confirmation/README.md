# Station 8 — Pico IR Confirmation

A receive-only Raspberry Pi Pico station. Every valid complete NEC IR frame turns
on a green confirmation LED for two seconds. The station does not transmit IR or
unlock a badge.

## Wiring

| Function | Pico GPIO | Physical pin | Connection |
|---|---:|---:|---|
| TSOP98638 output | GP16 | **Pin 21** | Receiver `OUT` |
| Green confirmation LED | GP15 | **Pin 20** | LED through 220–330 Ω resistor to GND |

Power the TSOP98638 from Pico 3.3 V and share ground. With the receiver lens
facing forward and its legs downward, verify the exact part datasheet before
wiring; the expected TSOP98638 connections are `OUT`, `GND`, and `VCC`.

Wire the green LED with its own current-limiting resistor:

```text
Pico physical pin 20 (GP15) -> 220–330 Ω -> LED anode
LED cathode -> Pico GND
```

## Behavior

1. The station starts with the green LED off.
2. It waits for any valid complete NEC frame.
3. When a frame is decoded, serial output prints its address and command.
4. Reception pauses and the green LED turns on for two seconds.
5. The LED turns off and reception resumes.

Malformed and incomplete frames do not light the LED. Frames received during the
two-second confirmation are intentionally ignored.

## Load

Copy these files to the Pico root using Thonny or `mpremote`:

- `main.py`
- `nec.py`
- `nec_codec.py`

Reset the Pico and monitor serial output.

## Test

Run the hardware-independent decoder tests from this folder:

```bash
python -m unittest discover -s tests -v
```

Physical IR reception and LED behavior must still be verified with the wired
Pico and the actual transmitting device.

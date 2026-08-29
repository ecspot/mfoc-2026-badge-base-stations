# Raspberry Pi Pico Base Station

Target: Raspberry Pi Pico running current MicroPython.

## Station roles

Set `STATION_ROLE` in [`config.py`](config.py) to one of these constants:

| Role constant | Behavior and trigger |
|---|---|
| `ROLE_RECEIVE_ONLY` | Initializes only the TSOP98638 receiver. Each complete NEC frame calls the `do_something(address, command)` serial stub in `main.py`. |
| `ROLE_RECEIVE_EVALUATE_UNLOCK` | Initializes receiver and transmitter. Badge advertisement command `0x01` or report commands `0x20`–`0x2F` trigger NEC unlock command `0x07` after the cooldown. |
| `ROLE_TRANSMIT_UNLOCK` | Initializes only the LTE-4208 transmitter. Sends unlock command `0x07` immediately and every `BROADCAST_INTERVAL_MS`. |

Example:

```python
from station_roles import ROLE_RECEIVE_EVALUATE_UNLOCK

STATION_ROLE = ROLE_RECEIVE_EVALUATE_UNLOCK
STATION_NUMBER = 1  # Valid values: 1..5
```

Here, `0x07` unlocks a Morse-code message on the badge. The station sends it as
an NEC command; it does not generate Morse timing.

## Assumed IR hardware

- **Emitter:** LITEON LTE-4208/LTE-4208M, 940 nm, typical 1.2 V forward voltage
  at 20 mA, 50 mA maximum continuous current, and 20° viewing angle.[6]
- **Receiver:** Vishay TSOP98638, 38 kHz demodulating receiver with a 2.0–3.6 V
  supply range and NEC compatibility.[2]

### Default pins

| Function | Pico GPIO | Physical pin | Connection |
|---|---:|---:|---|
| TSOP98638 output, pin 1 | GP16 | 21 | Receiver `OUT`; active-low demodulated signal |
| LTE-4208 transistor control | GP17 | 22 | About 1 kΩ to NPN base or logic-MOSFET gate network |
| Attraction/animation trigger | GP18 | 24 | 250 ms active-high 3.3 V logic pulse |
| Status LED | `LED` | On-board | On-board LED |
| TSOP98638 ground, pin 2 | GND | 23 or another GND | Common ground |
| TSOP98638 supply, pin 3 | 3V3(OUT) | 36 | **Never 5 V** |

Pico GPIO is **3.3 V only**. Do not feed a 5 V signal into GP16 or GP18. Check
component body orientation against the manufacturer drawing before wiring.[2]

### LTE-4208 driver

Do not drive the LTE-4208 directly from GP17. Use a low-side transistor driver:

```text
Supply -> LED series resistor -> LTE-4208 anode
LTE-4208 cathode -> transistor collector
transistor emitter -> GND
GP17 -> about 1 kΩ -> transistor base
Pico GND -> transmitter supply GND
```

For a 3.3 V LED supply, 1.2 V LED drop, and approximately 0.2 V transistor
saturation, start with **100 Ω for about 20 mA**. If the LED uses a separate
5 V supply, start with **180 Ω for about 20 mA**. Verify actual current and range
before increasing it; the LTE-4208's narrow beam makes alignment important.[6]

## Badge-carrier compatibility blocker

The retained badge reference firmware labels its carrier as 39 kHz but uses a
25 µs ON plus 26 µs OFF cycle at an 8 MHz configured CPU, which is approximately
19.6 kHz. A TSOP98638 is centered at 38 kHz, so receive-role compatibility with
a badge built from that exact source cannot be claimed.

Confirm a real badge's carrier with an oscilloscope or logic analyzer. This
project does not modify the badge firmware.

## Install and run

1. Flash a current MicroPython build onto the Pico.
2. Edit `config.py` to select the role and station number.
3. Copy these files to the Pico filesystem root:
   - `main.py`
   - `config.py`
   - `protocol.py`
   - `station_roles.py`
   - `nec.py`
   - `nec_codec.py`
4. Reset the Pico. MicroPython automatically runs `main.py`.
5. Open the USB serial console to view the configured role and NEC events.

Receive-only customization begins at `do_something()` in `main.py`.

## Extending the code

- Add badge commands, station addresses, and trigger rules in `protocol.py`.
- Add station-role capability rules in `station_roles.py`.
- Add received-command handling, NEC responses, GPIO actions, or serial actions
  in `main.py`.
- Replace the receive-only `do_something(address, command)` stub with the action
  required by an attraction.
- Keep NEC carrier and edge-timing changes isolated in `nec.py` and pure frame
  encoding/decoding changes in `nec_codec.py`.
- Add desktop tests under `tests/` for every new protocol, role, encoder, or
  decoder behavior.

## Tests

Run the pure protocol, station-role, encoder, and decoder suite under desktop
Python:

```bash
python -m unittest discover -s tests -v
```

Hardware timing, optical range, and badge interoperability still require a real
Pico, LTE-4208 transistor stage, TSOP98638, oscilloscope/logic analyzer, and
badge.

## Sources

[6] https://optoelectronics.liteon.com/upload/download/DS50-2005-011/LTE-4208M%20Data%20Sheet%20%28Rev1.0%29.PDF — Lite-On LTE-4208M datasheet

[2] https://www.vishay.com/docs/82832/tsop986.pdf — Vishay TSOP986 series datasheet
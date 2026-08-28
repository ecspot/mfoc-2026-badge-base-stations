# Raspberry Pi Pico Base Station

Target: Raspberry Pi Pico running MicroPython.

## Default pins

| Function | Pico GPIO | Physical pin | Connection |
|---|---:|---:|---|
| Demodulating IR receiver output | GP16 | 21 | Receiver module `OUT` |
| IR transmitter control | GP17 | 22 | Transistor/MOSFET input — **not directly to a high-current IR LED** |
| Attraction/animation trigger | GP18 | 24 | 250 ms active-high 3.3 V logic pulse |
| Status LED | `LED` | On-board | On-board LED |
| Ground | GND | 23 or another GND | Shared ground |
| Receiver power | 3V3(OUT) | 36 | Use a 3.3 V-compatible receiver/module |

Pico GPIO is **3.3 V only**. Do not feed a 5 V receiver output or animation-controller signal directly into a Pico pin.

Suggested transmitter stage: GP17 through about 1 kΩ to an NPN transistor base, emitter to GND, and collector switching an IR LED with a properly calculated current-limiting resistor.

## Configuration

Edit [`config.py`](config.py):

```python
STATION_NUMBER = 1  # 1..5
STATION_MODE = MODE_TRIGGERED
```

For continuous operation:

```python
STATION_MODE = MODE_CONTINUOUS
```

## Install and run

1. Flash a current MicroPython build onto the Pico.
2. Copy these files to the Pico filesystem root:
   - `main.py`
   - `config.py`
   - `protocol.py`
   - `nec.py`
   - `nec_codec.py`
3. Reset the Pico. MicroPython automatically runs `main.py`.
4. Open the USB serial console to view decoded and transmitted frames.

## Tests

The pure protocol and NEC decoder run under desktop Python:

```bash
python -m unittest discover -s tests -v
```

Hardware timing still requires testing with a real Pico, IR receiver, IR LED driver, and badge.

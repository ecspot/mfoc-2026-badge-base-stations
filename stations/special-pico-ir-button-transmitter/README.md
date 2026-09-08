# Special Pico IR Button Transmitter

A handheld or benchtop Raspberry Pi Pico utility that sends NEC command `0x01`
when its button is pressed. Receiver-equipped game stations use this command to
start their interactions.

Each accepted button press sends three complete NEC frames. Holding the button
does not continuously repeat transmissions; release it before pressing again.

## Wiring

| Function | Pico GPIO | Physical pin | Connection |
|---|---:|---:|---|
| Active-high button | GP16 | **Pin 21** | 3.3 V switched input with external 10 kΩ pull-down |
| IR transmitter control | GP15 | **Pin 20** | Transistor/MOSFET driver input |

### Button

```text
Pico 3.3 V ---- button switch ----+---- physical pin 21 (GP16)
                                  |
                                 10 kΩ
                                  |
Pico GND -------------------------+
```

Released is LOW and pressed is HIGH. Never apply 5 V to a Pico GPIO.

### IR transmitter

Use physical pin 20 only as the control signal for a transistor or logic-level
MOSFET driver:

```text
Physical pin 20 (GP15) -> approximately 1 kΩ -> transistor base/gate
Transistor emitter/source -> GND
5 V -> IR LED current-limiting resistor -> IR LED -> collector/drain
Pico GND -> transmitter supply GND
```

Do not power a high-current IR LED directly from GP15.

## Protocol

- Standard NEC address byte: `0x00` with inverse byte `0xFF`
- Raw 16-bit address field used by this implementation: `0xFF00`
- Command: `0x01`
- Command inverse: `0xFE`
- Complete 32-bit frame: `0xFE01FF00`
- Frames sent per press: 3

Game stations ignore the address when evaluating a badge trigger and start when
they receive command `0x01`.

## Load

Copy these files to the Pico root:

- `main.py`
- `station_logic.py`
- `nec.py`

Then reset the Pico. Serial output reports each button-triggered transmission.

## Test

```bash
python -m unittest discover -s tests -v
```

Physical carrier frequency, optical range, and reception by each game station
must still be verified with the real hardware.

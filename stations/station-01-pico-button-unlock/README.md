# Station 1 — Pico Button Unlock Transmitter

This is a self-contained, station-specific Raspberry Pi Pico deployment. It is
separate from the reusable `pico/` base code so Station 1 interaction changes do
not change any other base station.

## Locked behavior

- Platform: Raspberry Pi Pico with MicroPython.
- Station address: **`0xFB21`**.
- Unlock command: **`0x07`**.
- Role: transmit only; no IR receiver is initialized or required.
- Trigger: a normally-open push button connected between GP15 and GND.
- Idle: no NEC transmission. The program only samples the button.
- Success: releasing between 3 and 4 seconds sends one activation containing
  three complete extended-NEC frames and lights the green LED for 3 seconds.
- Early release: releasing before 3 seconds fails and lights the red LED for 2
  seconds.
- Overlong hold: reaching 4 seconds fails immediately and lights the red LED for
  2 seconds without transmitting.
- Re-arm: the button must be released stably for 30 ms before another hold can
  transmit.

## Wiring

### Button

| Button connection | Pico connection |
|---|---|
| One terminal | GP15, physical pin 20 |
| Other terminal | GND, physical pin 18 |

`main.py` enables GP15's internal pull-up. The button is therefore active-low
and needs no external pull-up resistor.

### LITEON LTE-4208 transmitter

| Function | Pico connection |
|---|---|
| Transmitter control | GP17, physical pin 22 |
| Ground | GND, physical pin 23 or another GND |
| Status | On-board LED |

### Result LEDs

Use a 220–330 Ω series resistor with each external LED.

| Function | Pico connection |
|---|---|
| Red failure LED | GP16, physical pin 21 |
| Green success LED | GP18, physical pin 24 |
| LED cathodes | GND, physical pin 23 or another GND |

Do not connect the LTE-4208 directly to GP17. Use the same current-limited
low-side transistor or logic-MOSFET driver described in [`../../pico/README.md`](../../pico/README.md).
A conservative 3.3 V starting circuit is GP17 through about 1 kΩ to an NPN base,
with a 100 Ω LED series resistor for approximately 20 mA. Verify actual current
and optical range on the assembled hardware.

## Load onto the Pico

1. Flash a current MicroPython build onto the Pico.
2. Copy all four runtime files from this directory to the Pico filesystem root:
   - `main.py`
   - `station_logic.py`
   - `nec.py`
   - `nec_codec.py`
3. Reset the Pico.
4. Open the USB serial console. It should print
   `Release between 3 and 4 seconds to unlock`.
5. Confirm that no IR activity occurs while the button is released.
6. Release before 3 seconds and confirm that the red LED lights without IR.
7. Release between 3 and 4 seconds and confirm that the green LED lights while
   one three-frame activation is transmitted.
8. Continue holding through 4 seconds and confirm that the red LED lights
   without IR, then release to re-arm the station.

## Desktop tests

From the repository root:

```bash
python -m unittest discover -s stations/station-01-pico-button-unlock/tests -v
```

The tests lock the address and command, verify the complete NEC frame value, and
verify both hold-time boundaries, failure suppression, and release/re-hold
behavior.

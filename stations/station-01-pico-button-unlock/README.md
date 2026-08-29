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
- Idle: no NEC transmission. The program only samples and debounces the button.
- Press: after 30 ms of stable contact, sends one activation containing three
  complete extended-NEC frames.
- Hold: does not repeat.
- Re-arm: the button must be released stably before another press can transmit.

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
4. Open the USB serial console. It should print `Waiting for button press`.
5. Confirm that no IR activity occurs while the button is released.
6. Press and hold the button. The status LED lights during one transmission.
7. Continue holding the button and confirm that it does not transmit again.
8. Release and press again to initiate the next transmission.

## Desktop tests

From the repository root:

```bash
python -m unittest discover -s stations/station-01-pico-button-unlock/tests -v
```

The tests lock the address and command, verify the complete NEC frame value, and
verify debounce, held-button suppression, and release/re-press behavior.

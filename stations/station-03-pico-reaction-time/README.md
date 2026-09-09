# Station 3 — Pico Reaction-Time Game

This is a self-contained Raspberry Pi Pico / MicroPython deployment. It receives
a badge trigger, runs a reaction-time interaction, and transmits the Station 3
unlock only after success.

## Locked identity

- Platform: Raspberry Pi Pico.
- Station address: **`0xFB23`**.
- Unlock command: **`0x07`**.
- Encoded extended-NEC frame: **`0xF807FB23`**.

## Interaction

1. The station starts idle and waits for a complete NEC badge frame.
2. Badge advertisement command `0x01` or report command `0x20`–`0x2F` arms a
   30-second game.
3. The reaction LED blinks three times, then turns off.
4. The reaction LED remains off for a random **2–5 seconds**.
5. When the LED turns on, the player has **750 ms** to press the button.
6. A successful press reports the measured reaction time, turns on the green
   success LED, sends three unlock frames, and returns to idle.

Pressing before the LED is a false start. The player must release the button,
a new random delay begins, and no unlock is transmitted. Missing the 750 ms
window turns on the red miss LED for three seconds. The red LED then turns off
and the next random attempt begins. A held button reports only once and must be
released before another press can register.

## Wiring

| Function | Pico GPIO | Connection |
|---|---:|---|
| TSOP98638 output | GP14 | Receiver `OUT`, active-low demodulated signal |
| Player button | GP15 | Normally-open button to GND; internal pull-up enabled |
| Red miss LED | GP16 | External LED through a 220–330 Ω resistor to GND |
| Green success LED | GP17 | External LED through a 220–330 Ω resistor to GND |
| LTE-4208 transmitter control | GP18 | Transistor/MOSFET driver input |
| Reaction/status LED | GP13 | External LED through a 220–330 Ω resistor to GND |

### IR hardware

- Power the TSOP98638 from Pico 3.3 V and share ground.
- Drive the LITEON LTE-4208 through a current-limited transistor or logic-MOSFET
  stage controlled by GP18. Do not drive the emitter at useful pulse current
  directly from GP18.
- The repository’s badge carrier compatibility warning still applies. Verify
  badge reception with the actual flashed badge and optical hardware.

## Deploy with Thonny

1. Install MicroPython on the Raspberry Pi Pico.
2. Connect the Pico and select its MicroPython interpreter in Thonny.
3. Copy these four files to the Pico root:
   - `main.py`
   - `station_logic.py`
   - `nec.py`
   - `nec_codec.py`
4. Reset the Pico.
5. Open the shell and confirm it prints `Station idle: waiting for badge`.

Pressing Thonny's Run button executes the open Mac file on the Pico as `<stdin>`;
it does not make sibling Mac files importable. Upload `station_logic.py`,
`nec.py`, and `nec_codec.py` to the Pico root before running a Mac copy of
`main.py`.

No sibling `pico/` directory is required on the device.

## Deploy with mpremote

From this Station 3 directory:

```bash
mpremote connect auto fs cp main.py :main.py
mpremote connect auto fs cp station_logic.py :station_logic.py
mpremote connect auto fs cp nec.py :nec.py
mpremote connect auto fs cp nec_codec.py :nec_codec.py
mpremote connect auto reset
```

## Test

The hardware-independent logic runs under normal CPython:

```bash
python -m unittest discover -s tests -v
```

The tests lock:

- address, command, and exact NEC frame;
- accepted badge trigger commands;
- random-delay bounds;
- 750 ms success boundary;
- false starts and missed-window retries;
- 30-second timeout;
- button debounce, held-button non-repeat, and release re-arming.

## Bench test sequence

1. Reset and confirm all visible LEDs are off while waiting for a badge.
2. Send a recognized badge frame and confirm the reaction LED blinks three times.
3. Confirm the reaction LED turns off for a random two-to-five-second delay.
4. Press before the reaction LED and confirm a false start.
5. Deliberately miss and confirm the red GP16 LED stays on for three seconds,
   then turns off as the next attempt begins.
6. Release, wait for `GO`, and press within 750 ms.
7. Confirm success reports the reaction time, turns on the green GP17 LED, and
   transmits three Station 3 unlock frames from GP18.
8. Send another badge trigger and confirm green turns off as the next game starts.
9. Arm again and do nothing; confirm the game times out after 30 seconds without
   transmitting.

Physical reaction timing, IR range, optical carrier compatibility, and badge
unlock behavior remain hardware-validation steps.

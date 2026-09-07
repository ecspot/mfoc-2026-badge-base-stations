# Station 3 — Pico Reaction-Time Game

This Raspberry Pi Pico station waits for a badge trigger, runs a three-round
reaction-time challenge, and transmits the Station 3 unlock after success.

## Locked identity

- Platform: Raspberry Pi Pico.
- Station address: **`0xFB24`**.
- Unlock command: **`0x07`**.
- Encoded extended-NEC frame: **`0xF807FB24`**.

## Interaction

1. The station waits for a recognized badge frame to start a 30-second game.
2. The reaction LED blinks three times, then turns off.
3. The reaction LED remains off for a random **2–5 seconds**.
4. When the LED turns on, the player has up to 750 ms to register a reaction.
5. Complete three measured reactions. Their combined time must be **under 730
   ms** to succeed.
6. Success turns on the green LED and transmits three Station 3 unlock frames.

Pressing before the LED is a false start. The player must release the button,
a new random delay begins, and no unlock is transmitted. A false start does not
count as one of the three measured reactions. Missing an individual 750 ms
window or reaching a three-reaction total of 730 ms or more turns on the red
miss LED and restarts the series. A held button reports only once and must be
released before another press can register.

## Wiring

| Function | Pico GPIO | Connection |
|---|---:|---|
| TSOP98638 output | GP14 | Receiver `OUT`, active-low demodulated signal |
| Player button | GP15 | Active-high button with external 10 kΩ pull-down |
| Red miss LED | GP16 | External LED through a 220–330 Ω resistor to GND |
| Green success LED | GP17 | External LED through a 220–330 Ω resistor to GND |
| LTE-4208 transmitter control | GP18 | Transistor/MOSFET driver input |
| Reaction/status LED | GP13 | External LED through a 220–330 Ω resistor to GND |

Wire the active-high player button as follows. GP15 reads LOW while released and
HIGH while pressed:

```text
Pico 3.3 V ---- button switch ----+---- GP15
                                  |
                                 10 kΩ
                                  |
Pico GND -------------------------+
```

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
5. Open the shell and confirm it reports `Station idle: waiting for badge`.

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
- three measured reactions with a combined time strictly under 730 ms;
- false starts and missed-window retries;
- 30-second timeout;
- button debounce, held-button non-repeat, and release re-arming.

## Bench test sequence

1. Reset and confirm all visible LEDs remain off while waiting for a badge.
2. Send a recognized badge frame and confirm the reaction LED blinks three times.
3. Confirm the reaction LED turns off for a random two-to-five-second delay.
4. Press before the reaction LED and confirm a false start.
5. Deliberately miss and confirm the red GP16 LED stays on for three seconds,
   then turns off as the next attempt begins.
6. Complete three reactions and confirm each time and the running total print.
7. Confirm a total below 730 ms turns on green GP17 and transmits three unlock
   frames from GP18.
8. Confirm a total of 730 ms or more lights red and restarts the series without
   transmitting.
9. Send another badge frame and confirm green turns off as the next game starts.
10. Start again and do nothing; confirm the game times out after 30 seconds.

Physical reaction timing, IR range, optical carrier compatibility, and badge
unlock behavior remain hardware-validation steps.

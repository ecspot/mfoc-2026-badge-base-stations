# Station 4 — Arduino Shadow-Light Game

This is a self-contained Arduino Uno/Nano deployment. It receives a badge
trigger, calibrates to local lighting, requires a cover–uncover–cover sequence,
and transmits the Station 4 unlock only after success.

## Locked identity

- Platform: Arduino Uno or ATmega328P Nano.
- Station address: **`0xFB28`**.
- Unlock command: **`0x07`**.
- Encoded extended-NEC frame: **`0xF807FB28`**.

## Interaction

1. The station starts idle with its visible LEDs off and waits for a complete
   NEC badge frame.
2. Badge advertisement command `0x01` or report command `0x20`–`0x2F` arms it.
3. The white illumination LED turns on. The player leaves the photoresistor
   uncovered during a **one-second calibration**.
4. The player completes this sequence:
   - Cover the sensor continuously for one second.
   - Uncover it continuously for one second.
   - Cover it continuously for one second.
5. Success sends three complete NEC frames using address `0xFB28` and command
   `0x07`, then returns to idle.

The calibrated covered threshold is 60% of the uncovered baseline. The uncovered
threshold is 80%, leaving a 20% hysteresis band that matches neither state. A
wrong or unstable light state resets only the current one-second hold. A
45-second overall timeout returns to idle without transmitting.

## Wiring

| Function | Arduino pin | Connection |
|---|---:|---|
| TSOP98638 output | D2 | Receiver `OUT`, active-low demodulated signal |
| LTE-4208 transmitter control | D3 | Transistor/MOSFET driver input |
| White illumination LED | D5 | LED through a suitable resistor to GND |
| Guide LED | D6 | LED through a suitable resistor to GND |
| Photoresistor divider | A0 | Divider midpoint |
| Step/status indication | D13 | On-board LED |

Wire the light-dependent resistor so brighter light gives a larger ADC value:

```text
Arduino 5 V -> photoresistor -> A0 -> 10 kΩ resistor -> GND
```

Place the D5 white LED so it illuminates the photoresistor consistently. Shield
the assembly from unrelated direct sunlight where practical.

Guide LED behavior:

- **On:** leave or make the sensor uncovered.
- **Off:** cover the sensor and cast a shadow.
- D13 flashes briefly when a step is accepted.

Use a current-limiting resistor for each visible LED; 220–330 Ω is a typical
starting range for common starter-kit LEDs.

### IR hardware

- Power the TSOP98638 from 3.3 V, not Arduino 5 V, and share ground.
- Drive the LITEON LTE-4208 through a current-limited transistor or logic-MOSFET
  stage. Do not drive it at useful pulse current directly from D3.
- The repository’s badge carrier compatibility warning still applies to
  physical badge-to-station reception.

## Option A: Arduino IDE

This workflow does not require PlatformIO:

1. Open
   [`Station04_Shadow_Light/Station04_Shadow_Light.ino`](Station04_Shadow_Light/Station04_Shadow_Light.ino)
   in Arduino IDE.
2. In **Tools > Manage Libraries**, install **IRremote** by Armin Joachimsmeyer,
   current 4.x release.
3. Select **Arduino Uno**, or the correct ATmega328P Nano processor option, and
   select the serial port.
4. Click **Verify**, then **Upload**.
5. Open Serial Monitor at **115200 baud**.

The `.ino`, `Station04App.cpp`, `Station04App.h`, and `StationLogic.h` form one
conventional Arduino sketch.

## Option B: VS Code with PlatformIO

This workflow does not require Arduino IDE:

1. Install VS Code and the PlatformIO IDE extension.
2. Open this `station-04-arduino-shadow-light` directory as the project folder.
3. Use **PlatformIO: Build**, **PlatformIO: Upload**, and **PlatformIO: Serial
   Monitor**.

Equivalent terminal commands from this directory are:

```bash
platformio run
platformio run --target upload
platformio device monitor --baud 115200
```

PlatformIO installs IRremote from `platformio.ini` and compiles the same sketch
sources used by Arduino IDE.

## Bench test sequence

1. Reset and confirm both external LEDs are off with no startup transmission.
2. Send a recognized badge frame. Leave the sensor uncovered while serial
   reports the one-second calibration.
3. Confirm the baseline is at least 200 ADC counts. If not, improve the white
   LED placement or reduce ambient shielding and re-arm.
4. Cover, uncover, and cover the sensor for one second each, following the guide
   LED and serial prompts.
5. Confirm serial reports Station 4 address `0xFB28`, command `0x07`, and three
   complete unlock frames only after the final step.
6. Repeat with unstable lighting and confirm the current hold resets without
   transmitting.
7. Let an armed game expire and confirm the 45-second timeout does not transmit.

Physical light thresholds, enclosure geometry, IR range, carrier compatibility,
and badge unlock behavior remain hardware-validation steps.

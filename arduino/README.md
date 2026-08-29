# Arduino Base Station

Target: Arduino Uno or ATmega328P Nano. The same source supports two independent
workflows: **Arduino IDE** or **VS Code with PlatformIO**. Use whichever tool is
more comfortable; neither workflow requires the other.

## Station roles

Each physical station is built with one role:

| Role | Arduino IDE selection | PlatformIO environment | Behavior and trigger |
|---|---|---|---|
| Receive only | `MFOC_ROLE_RECEIVE_ONLY` | `receive-only` | Receives any complete non-repeat NEC frame and calls the `doSomething(address, command)` serial stub. It never initializes the transmitter. |
| Receive, evaluate, unlock | `MFOC_ROLE_RECEIVE_EVALUATE_UNLOCK` | `receive-evaluate-unlock` | Receives NEC, recognizes badge advertisement command `0x01` or report commands `0x20`–`0x2F`, observes the cooldown, then sends unlock command `0x07`. |
| Transmit unlock only | `MFOC_ROLE_TRANSMIT_UNLOCK` | `transmit-unlock` | Never initializes the receiver. It sends unlock command `0x07` immediately at startup and every `BROADCAST_INTERVAL_MS`. |

Here, `0x07` is the badge command that unlocks a Morse-code message. The base
station sends `0x07` as an NEC command; it does not transmit Morse timing.

## Assumed IR hardware

- **Emitter:** LITEON LTE-4208/LTE-4208M, 940 nm. The manufacturer specifies a
  typical 1.2 V forward voltage at 20 mA, 50 mA maximum continuous current, and
  a narrow 20° viewing angle.[6]
- **Receiver:** Vishay TSOP98638, a 38 kHz demodulating receiver intended for
  NEC and related remote-control protocols. Its supply range is **2.0–3.6 V**;
  do not power it from the Arduino 5 V pin.[2]

### Default pins

| Function | Arduino pin | Connection |
|---|---:|---|
| TSOP98638 output, pin 1 | D2 | Receiver `OUT`; active-low demodulated signal |
| LTE-4208 transistor control | D3 | About 1 kΩ to NPN base or logic-MOSFET gate network |
| Attraction/animation trigger | D4 | 250 ms active-high logic pulse |
| Status LED | D13 / `LED_BUILTIN` | On-board LED |
| TSOP98638 ground, pin 2 | GND | Common ground |
| TSOP98638 supply, pin 3 | 3.3V | **Never 5 V** |

Check the component body orientation against the manufacturer drawing before
wiring; the table uses Vishay's electrical pin numbering.[2]

### LTE-4208 driver

Do not drive the LTE-4208 directly from D3. A basic low-side NPN stage is:

```text
Supply -> LED series resistor -> LTE-4208 anode
LTE-4208 cathode -> transistor collector
transistor emitter -> GND
D3 -> about 1 kΩ -> transistor base
Arduino GND -> transmitter supply GND
```

Starting LED-resistor values, assuming LTE-4208 `VF = 1.2 V` and approximately
`0.2 V` transistor saturation, are:

| LED supply | Target pulse current | Calculated | Conservative standard value |
|---:|---:|---:|---:|
| 3.3 V | 20 mA | 95 Ω | 100 Ω |
| 5 V | 20 mA | 180 Ω | 180 Ω |
| 3.3 V | 40 mA | 47.5 Ω | 51 Ω |
| 5 V | 40 mA | 90 Ω | 100 Ω |

Start at 20 mA, verify current and optical range, and only increase it within
the LED, resistor, transistor, supply, and thermal ratings. The LTE-4208 has a
narrow beam, so mechanical alignment matters.[6]

## Badge-carrier compatibility blocker

The retained badge reference firmware labels its carrier as 39 kHz, but
`gpio_ir_nec.c` drives the LED for 25 µs and turns it off for 26 µs per cycle
while the project is configured for an 8 MHz CPU. That is approximately
19.6 kHz, not 39 kHz. A TSOP98638 is centered at 38 kHz, so receive-role
compatibility with a badge built from that exact source cannot be claimed.

This is an optical front-end issue, not an NEC address/command software issue.
Confirm the carrier from a real badge using an oscilloscope or logic analyzer.
The badge repository remains read-only and is not modified by this project.

## Option A: Arduino IDE

Use this path without PlatformIO:

1. Open
   [`MFOC_Badge_Base_Station/MFOC_Badge_Base_Station.ino`](MFOC_Badge_Base_Station/MFOC_Badge_Base_Station.ino)
   in Arduino IDE. Keep the enclosing folder name unchanged so it matches the
   `.ino` filename.
2. Open **Tools > Manage Libraries**, search for **IRremote by Armin
   Joachimsmeyer**, and install a current 4.x release.
3. Open the `config.h` tab and choose a role by setting:

   ```cpp
   #define MFOC_STATION_ROLE MFOC_ROLE_RECEIVE_EVALUATE_UNLOCK
   ```

   Substitute `MFOC_ROLE_RECEIVE_ONLY` or `MFOC_ROLE_TRANSMIT_UNLOCK` for the
   other station types.
4. In the same file, set the one-hot message station:

   ```cpp
   constexpr uint8_t STATION_NUMBER = 1;  // 1..5
   ```

5. Select **Tools > Board > Arduino Uno**, or the correct ATmega328P Nano
   processor option, then select the serial port.
6. Click **Verify**. If it succeeds, click **Upload**.
7. Open **Tools > Serial Monitor** at **115200 baud** to see role, receive, and
   transmit events.

Arduino IDE displays the `.ino`, `BaseStation.cpp`, `BaseStation.h`, `config.h`,
`protocol.h`, and `StationRoles.h` as one conventional sketch.

## Option B: VS Code with PlatformIO

Use this path without Arduino IDE:

1. Install VS Code and the **PlatformIO IDE** extension.
2. In VS Code, open this `arduino` directory as the project folder. PlatformIO
   reads [`platformio.ini`](platformio.ini) and installs Arduino-IRremote
   automatically.
3. Set `STATION_NUMBER` in
   [`MFOC_Badge_Base_Station/config.h`](MFOC_Badge_Base_Station/config.h).
4. Choose the required PlatformIO environment:
   - `receive-only`
   - `receive-evaluate-unlock`
   - `transmit-unlock`
5. Use **PlatformIO: Build**, **PlatformIO: Upload**, and **PlatformIO: Serial
   Monitor** from VS Code, or run the equivalent terminal commands from this
   directory:

   ```bash
   platformio run -e receive-only
   platformio run -e receive-only --target upload
   platformio device monitor --baud 115200
   ```

   Replace `receive-only` with either other environment as needed.

To compile all three variants without uploading:

```bash
platformio run -e receive-only -e receive-evaluate-unlock -e transmit-unlock
```

PlatformIO's environment build flag selects the role and overrides the default
role in `config.h`. Both workflows compile the same sketch implementation.

## Extending the code

- Add badge commands, station addresses, and trigger rules in `protocol.h`.
- Add station-role capability rules in `StationRoles.h`.
- Add received-command handling, NEC responses, GPIO actions, or serial actions
  in `BaseStation.cpp`.
- Replace the receive-only `doSomething(address, command)` stub with the action
  required by an attraction.
- Add a PlatformIO environment for each new deployable role so every variant is
  compiled independently.
- Add compile-time assertions under `tests/` for new protocol and role rules.

## Files

- `MFOC_Badge_Base_Station/MFOC_Badge_Base_Station.ino` — Arduino `setup()` and `loop()`.
- `MFOC_Badge_Base_Station/BaseStation.cpp` — station behavior and receive-only extension stub.
- `MFOC_Badge_Base_Station/BaseStation.h` — interface used by the sketch.
- `MFOC_Badge_Base_Station/config.h` — pins, role, station number, and timing.
- `MFOC_Badge_Base_Station/protocol.h` — badge commands and station addresses.
- `MFOC_Badge_Base_Station/StationRoles.h` — tested role decisions.
- `platformio.ini` — PlatformIO environments and IRremote dependency.
- `tests/` — compile-time protocol and role tests.

## Sources

[6] https://optoelectronics.liteon.com/upload/download/DS50-2005-011/LTE-4208M%20Data%20Sheet%20%28Rev1.0%29.PDF — Lite-On LTE-4208M datasheet

[2] https://www.vishay.com/docs/82832/tsop986.pdf — Vishay TSOP986 series datasheet
# Station 2 — Arduino Servo Target

This is a self-contained, station-specific Arduino Uno/Nano deployment. It is
separate from the reusable `arduino/` base code so changes to this target game
do not change other base stations.

## Locked identity

- Platform: Arduino Uno or ATmega328P Nano.
- Station address: **`0xFB22`**.
- Unlock command: **`0x07`**.
- Encoded extended-NEC frame: **`0xF807FB22`**.

## Interaction

1. The station starts idle with its servo detached and waits for a complete NEC
   badge frame.
2. Badge advertisement command `0x01` or report command `0x20`–`0x2F` arms the
   station.
3. The servo attaches and sweeps a pointer from 20° to 160° and back at one
   degree every 20 ms.
4. The player presses the button while the pointer is in the physically marked
   **80°–100° success zone**.
5. A successful press sends three complete NEC frames using address `0xFB22`
   and command `0x07`, detaches the servo, and returns to idle.

A press outside the marked zone flashes the status LED, prints the missed angle,
and keeps the station armed. The player must release the button before trying
again. A button already held when the badge arrives is ignored until released.
If no success occurs within 30 seconds, the station detaches the servo and
returns to idle without transmitting.

## Wiring

| Function | Arduino pin | Connection |
|---|---:|---|
| TSOP98638 output | D2 | Receiver `OUT`, active-low demodulated signal |
| LTE-4208 transmitter control | D3 | Transistor/MOSFET driver input |
| Servo signal | D5 | Orange/yellow/white servo signal lead |
| Player button | D6 | Normally-open button to GND; internal pull-up enabled |
| Status | D13 / `LED_BUILTIN` | On-board LED |

### Servo power

Do not power a moving or loaded servo from an Arduino I/O pin. Prefer a separate
regulated 5 V supply sized for the servo's stall current:

```text
External 5 V +  -> servo red power lead
External GND    -> servo brown/black ground lead
Arduino GND     -> external GND
Arduino D5      -> servo signal lead
```

The Arduino and servo supply must share ground. Add local bulk capacitance near
the servo supply connection; a starting point for a small hobby servo is 470 µF
plus a 0.1 µF ceramic capacitor. Do not connect an external 5 V supply to the
Arduino 5 V pin unless the complete power design intentionally supports that
connection.

### IR hardware

- Power the TSOP98638 from 3.3 V, not Arduino 5 V, and share ground.
- Drive the LITEON LTE-4208 through a current-limited transistor or logic-MOSFET
  stage. Do not drive the emitter at useful pulse current directly from D3.
- Follow the electrical details in [`../../arduino/README.md`](../../arduino/README.md).

The badge carrier discrepancy documented in the repository root still applies
to physical receive testing. Confirm the actual badge carrier before treating
badge-to-station reception as validated.

## Mechanical setup

1. Attach the servo horn while the servo is near 90°.
2. Attach a lightweight pointer or target arm.
3. Mark the success region corresponding to servo angles 80° through 100°.
4. Ensure the pointer can safely travel from 20° to 160° without binding.
5. If the linkage cannot support that range, adjust the station-local constants
   in `StationLogic.h` and its compile-time tests together.

Do not attach a heavy or sharp object to the servo horn. Guard the moving area
so visitors cannot pinch fingers in the mechanism.

## Option A: Arduino IDE

This workflow does not require PlatformIO:

1. Open
   [`Station02_Servo_Target/Station02_Servo_Target.ino`](Station02_Servo_Target/Station02_Servo_Target.ino)
   in Arduino IDE.
2. In **Tools > Manage Libraries**, install:
   - **IRremote** by Armin Joachimsmeyer, current 4.x release.
   - **Servo** by Arduino.
3. Select **Arduino Uno**, or the correct ATmega328P Nano processor option, and
   select the serial port.
4. Click **Verify**, then **Upload**.
5. Open Serial Monitor at **115200 baud**.

The `.ino`, `Station02App.cpp`, `Station02App.h`, and `StationLogic.h` form one
conventional Arduino sketch and appear as sketch tabs.

## Option B: VS Code with PlatformIO

This workflow does not require Arduino IDE:

1. Install VS Code and the PlatformIO IDE extension.
2. Open this `station-02-arduino-servo-target` directory as the project folder.
3. Use **PlatformIO: Build**, **PlatformIO: Upload**, and **PlatformIO: Serial
   Monitor**.

Equivalent terminal commands from this directory are:

```bash
platformio run
platformio run --target upload
platformio device monitor --baud 115200
```

PlatformIO installs both IRremote and Servo from `platformio.ini` and compiles
the same sketch sources used by Arduino IDE.

## Bench test sequence

1. Reset the station and confirm serial prints `Station idle: waiting for badge`.
2. Send a recognized badge frame and confirm the status LED turns on and the
   servo begins sweeping.
3. Press outside 80°–100° and confirm no IR unlock transmission occurs.
4. Release the button, then press inside 80°–100°.
5. Confirm serial reports `SUCCESS` followed by Station 2 address `0xFB22` and
   command `0x07`.
6. Confirm the servo detaches and the station waits for the next badge.
7. Arm again without succeeding and confirm the 30-second timeout returns it to
   idle without transmitting.

## Files

- `Station02_Servo_Target/Station02_Servo_Target.ino` — Arduino entry points.
- `Station02_Servo_Target/Station02App.cpp` — hardware and interaction runtime.
- `Station02_Servo_Target/Station02App.h` — sketch/application interface.
- `Station02_Servo_Target/StationLogic.h` — locked protocol and tested decisions.
- `tests/station_logic_test.cpp` — compile-time identity and interaction checks.
- `platformio.ini` — Uno target and library dependencies.

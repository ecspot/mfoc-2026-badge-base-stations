# Station 2 — Arduino Servo Target

This is a self-contained, station-specific Arduino Uno R3 deployment. This
temporary bench-test build starts automatically and does not initialize IR
reception or transmission.

## Locked identity

- Platform: **Arduino Uno R3**.
- Station address: **`0xFB22`**.
- Unlock command: **`0x07`**.
- Encoded extended-NEC frame: **`0xF807FB22`**.

## Interaction

1. Resetting the Arduino arms the game automatically without a badge.
2. The servo attaches and sweeps a pointer from 20° to 160° and back at one
   degree every 12 ms.
3. The player presses the button while the pointer is in the physically marked
   **85°–95° success zone**.
4. A successful press reports the angle, transmits nothing, detaches the servo,
   and waits for an Arduino reset.

A press outside the marked zone flashes the status LED, prints the missed angle,
and keeps the station armed. The player must release the button before trying
again. A button already held when the game starts is ignored until released.
If no success occurs within 30 seconds, the station detaches the servo and
returns to idle without transmitting.

## Wiring

| Function | Arduino pin | Connection |
|---|---:|---|
| TSOP98638 output | D2 | Receiver `OUT`, active-low demodulated signal |
| LTE-4208 transmitter control | D3 | Transistor/MOSFET driver input |
| Servo signal | D5 | Orange/yellow/white servo signal lead |
| Player button | D6 | Normally-open button to GND; internal pull-up enabled |
| Status LED | D7 | External LED through a 220–330 Ω resistor to GND |

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

The bench-test build does not initialize D2 or D3, so the IR receiver and
transmitter are not required while testing the servo, button, and external D7
status LED. Production firmware will restore the IR hardware and badge gating.

The badge carrier discrepancy documented in the repository root still applies
to physical receive testing. Confirm the actual badge carrier before treating
badge-to-station reception as validated.

## Mechanical setup

1. Attach the servo horn while the servo is near 90°.
2. Attach a lightweight pointer or target arm.
3. Mark the success region corresponding to servo angles 85° through 95°.
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
   - **Servo** by Arduino.
3. Select **Arduino Uno** and select the serial port.
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

PlatformIO targets `uno`, installs Servo from `platformio.ini`, and
compiles the same sketch sources used by Arduino IDE. IRremote is not required
by the temporary bench build.

## Bench test sequence

1. Reset the station and confirm serial reports bench-test mode and immediately
   arms the game.
2. Confirm the external D7 status LED turns on and the servo begins sweeping.
3. Press outside 85°–95° and confirm serial reports the missed angle while the
   game remains active.
4. Release the button, then press inside 85°–95°.
5. Confirm serial reports `SUCCESS` and that no IR transmission occurs.
6. Confirm the servo detaches and the status LED turns off. Reset to play again.
7. Reset and let the game run without succeeding; confirm the 30-second timeout
   detaches the servo and turns the status LED off.

## Files

- `Station02_Servo_Target/Station02_Servo_Target.ino` — Arduino entry points.
- `Station02_Servo_Target/Station02App.cpp` — hardware and interaction runtime.
- `Station02_Servo_Target/Station02App.h` — sketch/application interface.
- `Station02_Servo_Target/StationLogic.h` — locked protocol and tested decisions.
- `tests/station_logic_test.cpp` — compile-time identity and interaction checks.
- `platformio.ini` — Uno target and library dependencies.

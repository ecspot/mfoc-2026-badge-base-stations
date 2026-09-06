# Station 2 — Arduino Servo Target

This is a self-contained, station-specific Arduino Uno R3 deployment. It waits
for a badge announcement, runs the servo target game, and transmits the Station
2 unlock after success.

## Locked identity

- Platform: **Arduino Uno R3**.
- Station address: **`0xFB22`**.
- Unlock command: **`0x07`**.
- Encoded extended-NEC frame: **`0xF807FB22`**.

## Interaction

1. The station waits idle until it receives a complete NEC badge advertisement
   command `0x01` or report command `0x20`–`0x2F`.
2. The servo attaches and sweeps a pointer from 20° to 160° and back at one
   degree every 9 ms.
3. The player presses the button while the pointer is in the physically marked
   **85°–95° success zone**.
4. A successful press reports the angle, detaches the servo, lights the green
   D7 LED, and transmits three Station 2 unlock frames. The green LED remains on
   for three seconds before the station returns to idle.

A press outside the marked zone pauses the servo for 250 ms, prints the missed
angle, and keeps the station armed; the green success LED remains off. The
player must release the button before trying again. A button already held when
the game starts is ignored until released.
If no success occurs within 30 seconds, the station detaches the servo and
returns to idle without transmitting.

## Wiring

| Function | Arduino pin | Connection |
|---|---:|---|
| TSOP98638 output | D2 | Receiver `OUT`, active-low demodulated signal |
| LTE-4208 transmitter control | D3 | Transistor/MOSFET driver input |
| Servo signal | D5 | Orange/yellow/white servo signal lead |
| Player button | D6 | Active-high switched 5 V input with 10 kΩ pull-down to GND |
| Green success LED | D7 | External LED through a 220–330 Ω resistor to GND |

### Illuminated player button

The button input is active-high. D6 reads HIGH when the button connects it to
5 V and requires an external 10 kΩ pull-down so it reads LOW when released:

```text
Arduino 5 V ---- button switch ----+---- Arduino D6
                                   |
                                  10 kΩ
                                   |
Arduino GND -----------------------+

Arduino 5 V ---- button LED anode
Arduino GND ---- button LED cathode
```

If the button LED does not include a resistor rated for 5 V, add a 220–330 Ω
series resistor in its LED branch. Keep that LED resistor out of the D6 signal
path.

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

The station receives badge announcements through D2 and transmits the Station 2
unlock through D3. The D3 output should control an appropriate transistor or
MOSFET driver for the IR LED rather than powering the emitter directly.

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
   - **IRremote** by Armin Joachimsmeyer.
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

PlatformIO targets `uno`, installs IRremote and Servo from `platformio.ini`, and
compiles the same sketch sources used by Arduino IDE.

## Test sequence

1. Reset the station and confirm it reports that it is waiting for a badge. The
   servo and green D7 LED should remain off.
2. Send a recognized badge announcement and confirm the servo begins sweeping
   while D7 remains off.
3. Press outside 85°–95° and confirm the servo pauses for 250 ms and serial
   reports the missed angle while the game remains active.
4. Release the button, then press inside 85°–95°.
5. Confirm serial reports `SUCCESS`, the servo detaches, D7 lights for three
   seconds, and three unlock frames are transmitted.
6. Confirm D7 turns off and the station waits for the next badge announcement.
7. Start another game and let it run without succeeding; confirm the 30-second
   timeout detaches the servo and leaves D7 off.

## Files

- `Station02_Servo_Target/Station02_Servo_Target.ino` — Arduino entry points.
- `Station02_Servo_Target/Station02App.cpp` — hardware and interaction runtime.
- `Station02_Servo_Target/Station02App.h` — sketch/application interface.
- `Station02_Servo_Target/StationLogic.h` — locked protocol and tested decisions.
- `tests/station_logic_test.cpp` — compile-time identity and interaction checks.
- `platformio.ini` — Uno target and library dependencies.

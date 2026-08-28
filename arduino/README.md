# Arduino Base Station

Target: Arduino Uno or Nano (ATmega328P), using Arduino IDE or PlatformIO.

## Default pins

| Function | Arduino pin | Connection |
|---|---:|---|
| Demodulating IR receiver output | D2 | Receiver module `OUT` |
| IR transmitter control | D3 | Transistor/MOSFET input — **not directly to a high-current IR LED** |
| Attraction/animation trigger | D4 | 250 ms active-high logic pulse |
| Status LED | D13 / `LED_BUILTIN` | On-board LED |

Receiver power: connect `GND` to Arduino GND and `VCC` according to the receiver module rating. All external controller grounds must be common unless isolated.

Suggested transmitter stage: D3 through about 1 kΩ to an NPN transistor base, emitter to GND, and collector switching an IR LED with a properly calculated current-limiting resistor.

## Configuration

Edit [`MFOC_Badge_Base_Station/config.h`](MFOC_Badge_Base_Station/config.h):

```cpp
constexpr uint8_t STATION_NUMBER = 1;  // 1..5
constexpr StationMode STATION_MODE = StationMode::TriggeredResponse;
```

For continuous operation:

```cpp
constexpr StationMode STATION_MODE = StationMode::ContinuousBroadcast;
```

## Arduino IDE

1. Open
   [`MFOC_Badge_Base_Station/MFOC_Badge_Base_Station.ino`](MFOC_Badge_Base_Station/MFOC_Badge_Base_Station.ino)
   in Arduino IDE. Keep the enclosing folder name unchanged so it matches the
   `.ino` filename.
2. The sketch tab contains the real Arduino `setup()` and `loop()` entry points.
   They call the implementation in `BaseStation.cpp` through `BaseStation.h`.
3. In Library Manager, install **IRremote** by Armin Joachimsmeyer.
4. Select **Arduino Uno** or the appropriate ATmega328P Nano board and port.
5. Click **Verify**, then **Upload**.

All Arduino source files are in the same conventional sketch folder and are
shown as tabs in Arduino IDE. PlatformIO builds that same folder.

## PlatformIO build and upload

From this folder:

```bash
platformio run
platformio run --target upload
platformio device monitor
```

Serial speed is 115200 baud. The firmware logs every decoded NEC frame and every unlock transmission.

## Files

- `MFOC_Badge_Base_Station/MFOC_Badge_Base_Station.ino` — `setup()` and `loop()`.
- `MFOC_Badge_Base_Station/BaseStation.cpp` — station implementation.
- `MFOC_Badge_Base_Station/BaseStation.h` — interface used by the sketch.
- `MFOC_Badge_Base_Station/config.h` — pins, mode, station number, and timing.
- `MFOC_Badge_Base_Station/protocol.h` — protocol constants and trigger recognition.
- `platformio.ini` — Uno target and Arduino-IRremote dependency.
- `tests/protocol_test.cpp` — host-readable protocol assertions.

# MFOC 2026 Badge Base Stations — Alpha

This folder is the source of truth for the base-station project.

## Codebases

- [`arduino/`](arduino/) — Arduino C++ for Uno/Nano using Arduino-IRremote.
- [`pico/`](pico/) — MicroPython for Raspberry Pi Pico.
- [`stations/`](stations/) — isolated, ready-to-load implementations for
  specific physical stations.

## Specific stations

| Station | Platform | Locked address | Trigger and behavior |
|---|---|---:|---|
| [Station 1](stations/station-01-pico-button-unlock/) | Raspberry Pi Pico | `0xFB21` | A continuous 3-second button hold sends unlock command `0x07`; early release cancels and continued holding does not repeat. |
| [Station 2](stations/station-02-arduino-servo-target/) | Arduino Uno/Nano | `0xFB22` | A badge arms a sweeping servo target; a button press in the 80°–100° zone sends unlock command `0x07`. |
| [Station 3](stations/station-03-pico-reaction-time/) | Raspberry Pi Pico | `0xFB24` | A badge arms a reaction game; pressing within 750 ms of a random LED signal sends unlock command `0x07`. |
| [Station 4](stations/station-04-arduino-shadow-light/) | Arduino Uno/Nano | `0xFB28` | A badge starts light calibration; completing cover–uncover–cover sends unlock command `0x07`. |
| [Station 5](stations/station-05-pico-stepper-safecracker/) | Raspberry Pi Pico | `0xFB30` | Memorize and enter three 3–5 digit codes using a stepper dial, one-digit display, and Up/Down/Select buttons. |
| [Station 6](stations/station-06-pico-ultrasonic-distance/) | Raspberry Pi Pico | `0xFB40` | Hold a hand in three prompted ultrasonic distance zones for 750 ms each. |
| [Station 7](stations/station-07-pico-simon-memory/) | Raspberry Pi Pico | `0xFB80` | Repeat four growing Simon light/button sequences to unlock. |
| [Station 8](stations/station-08-pico-ir-confirmation/) | Raspberry Pi Pico | N/A | Receive any valid complete NEC frame and light a green confirmation LED for two seconds. |

Both implementations provide:

- NEC IR reception from badges.
- A receive-only role with an explicit attraction-specific extension stub.
- A receive/evaluate/unlock role for badge advertisement command `0x01` and report commands `0x20`–`0x2F`.
- A transmit-only periodic unlock role that does not initialize a receiver.
- Unlock transmission using command `0x07`.
- A configurable station number from 1 through 7, mapped to the registered one-hot address sequence.
- A timed digital output pulse for an attraction/animation controller.
- Serial logging of received and transmitted frames.

## Protocol used by this alpha

| Purpose | Value |
|---|---:|
| Badge advertisement trigger | Command `0x01` |
| Badge report trigger | Commands `0x20`–`0x2F` |
| Base-station unlock command | `0x07` |
| Station 1 address | `0xFB21` |
| Station 2 address | `0xFB22` |
| Station 3 address | `0xFB24` |
| Station 4 address | `0xFB28` |
| Station 5 address | `0xFB30` |
| Station 6 address | `0xFB40` |
| Station 7 address | `0xFB80` |

The station sends three complete NEC frames per activation. It does not use abbreviated NEC repeat frames because the badge receiver expects address and command fields.

The assumed optical parts are a LITEON LTE-4208 940 nm emitter and Vishay
TSOP98638 38 kHz demodulating receiver. See the platform READMEs for transistor
driver, 3.3 V receiver-power, resistor, role-selection, and toolchain details.

## Important badge-firmware compatibility note

The badge source was used as **read-only protocol reference** and is not part of this project. Its current unlock condition is:

```c
(nec_input_address & 0xFFD0) == 0xFB20
```

That comparison cannot be true because mask `0xFFD0` clears bit `0x0020` while the comparison requires that bit. These base stations send the apparently intended one-hot addresses listed above, but a badge running that exact source revision will not accept them. Per project scope, no badge firmware file is changed here. This should be confirmed against the firmware actually flashed on test badges during hardware testing.

The same reference firmware labels its emitter carrier as 39 kHz but implements
a 25 µs ON plus 26 µs OFF cycle with an 8 MHz configured CPU, or approximately
19.6 kHz. That is not compatible on paper with a 38 kHz-centered TSOP98638.
Measure a real badge before treating either receive role as hardware-validated.

## Hardware caution

Do **not** power a high-current IR LED directly from a GPIO pin. Use a transistor/MOSFET driver, a current-limiting resistor, and a shared ground. The attraction pin is a logic signal only; use an optocoupler or level shifter if the animation controller requires it.

See each codebase README for exact pins, wiring, configuration, and run instructions.

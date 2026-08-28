# MFOC 2026 Badge Base Stations — Alpha

This folder is the source of truth for the base-station project.

## Codebases

- [`arduino/`](arduino/) — Arduino C++ for Uno/Nano using Arduino-IRremote.
- [`pico/`](pico/) — MicroPython for Raspberry Pi Pico.

Both implementations provide:

- NEC IR reception from badges.
- Triggered-response mode for badge advertisement command `0x01` and report commands `0x20`–`0x2F`.
- Continuous-broadcast mode.
- Unlock transmission using command `0x07`.
- A configurable station number from 1 through 5, encoded as a one-hot address flag.
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

The station sends three complete NEC frames per activation. It does not use abbreviated NEC repeat frames because the badge receiver expects address and command fields.

## Important badge-firmware compatibility note

The badge source was used as **read-only protocol reference** and is not part of this project. Its current unlock condition is:

```c
(nec_input_address & 0xFFD0) == 0xFB20
```

That comparison cannot be true because mask `0xFFD0` clears bit `0x0020` while the comparison requires that bit. These base stations send the apparently intended one-hot addresses listed above, but a badge running that exact source revision will not accept them. Per project scope, no badge firmware file is changed here. This should be confirmed against the firmware actually flashed on test badges during hardware testing.

## Hardware caution

Do **not** power a high-current IR LED directly from a GPIO pin. Use a transistor/MOSFET driver, a current-limiting resistor, and a shared ground. The attraction pin is a logic signal only; use an optocoupler or level shifter if the animation controller requires it.

See each codebase README for exact pins, wiring, configuration, and run instructions.

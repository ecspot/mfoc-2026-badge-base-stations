# Specific Base Stations

Each directory here is a self-contained deployable station. Station-specific
interaction code stays here rather than changing the reusable `arduino/` or
`pico/` base implementations.

| Station | Platform | Address | Trigger | Deployment |
|---|---|---:|---|---|
| 1 | Raspberry Pi Pico | `0xFB21` | 3-second button hold | [`station-01-pico-button-unlock/`](station-01-pico-button-unlock/) |
| 2 | Arduino Uno/Nano | `0xFB22` | Receive badge, stop servo target with button | [`station-02-arduino-servo-target/`](station-02-arduino-servo-target/) |
| 3 | Raspberry Pi Pico | `0xFB24` | Receive badge, react to a random LED signal | [`station-03-pico-reaction-time/`](station-03-pico-reaction-time/) |
| 4 | Arduino Uno/Nano | `0xFB28` | Receive badge, complete cover–uncover–cover light sequence | [`station-04-arduino-shadow-light/`](station-04-arduino-shadow-light/) |
| 5A | Raspberry Pi Pico | `0xFB30` | Enter three generated codes with stepper dial and display | [`station-05-pico-stepper-safecracker/`](station-05-pico-stepper-safecracker/) |
| 5B | Raspberry Pi Pico | `0xFB30` | Complete three prompted ultrasonic distance zones | [`station-05b-pico-ultrasonic-distance/`](station-05b-pico-ultrasonic-distance/) |
| 5C | Raspberry Pi Pico | `0xFB30` | Complete four Simon memory rounds | [`station-05c-pico-simon-memory/`](station-05c-pico-simon-memory/) |

Stations 5A–5C are alternative game deployments for the same fifth badge
achievement. The current badge protocol has five one-hot achievement bits and
cannot represent three additional independent achievements without a future
badge/protocol change.

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
| 5 | Raspberry Pi Pico | `0xFB30` | Enter three generated codes with stepper dial and display | [`station-05-pico-stepper-safecracker/`](station-05-pico-stepper-safecracker/) |
| 6 | Raspberry Pi Pico | `0xFB40` | Complete three prompted ultrasonic distance zones | [`station-06-pico-ultrasonic-distance/`](station-06-pico-ultrasonic-distance/) |
| 7 | Raspberry Pi Pico | `0xFB80` | Complete four Simon memory rounds | [`station-07-pico-simon-memory/`](station-07-pico-simon-memory/) |
| 8 | Raspberry Pi Pico | N/A | Receive NEC command `0x01` and light a confirmation LED | [`station-08-pico-ir-confirmation/`](station-08-pico-ir-confirmation/) |

Stations 5, 6, and 7 are independent deployments with unique fixed addresses.
Confirm that the badge firmware flashed for the event includes the registered
Station 6 and Station 7 achievement bits; badge firmware is outside this repo.
Station 8 is receive-only and does not have or transmit an unlock address.

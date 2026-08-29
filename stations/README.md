# Specific Base Stations

Each directory here is a self-contained deployable station. Station-specific
interaction code stays here rather than changing the reusable `arduino/` or
`pico/` base implementations.

| Station | Platform | Address | Trigger | Deployment |
|---|---|---:|---|---|
| 1 | Raspberry Pi Pico | `0xFB21` | 3-second button hold | [`station-01-pico-button-unlock/`](station-01-pico-button-unlock/) |

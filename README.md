# Personal Probabalistic Actor Pinging (PPAP)

## Description
This code is accompanying the result of the lecture "Digital Making PR" from 2026S. We, Sebastian Kirner and Maximilian Kainz, created a sophisticated framework to track a target device. Currently, only Bluetooth RSSI is implemented as a means to track the device, but the software is created in a way that more technologies are implementable. 

## Installation
1. Download a copy of this repository
2. Open a terminal in the subfolder `./esp32`.
3. Start a development shell by running `nix develop --extra-experimental-features
nix-command --extra-experimental-features flakes`. NixOS or the Nix package manager must be installed. This will load all dependencies of the ESP32 and therefore take a while the first time.
4. Connect an ESP32 via USB to your PC.
5. Update/Create the `.env` file containing the parameters WIFI_NAME and WIFI_PASSWORD with the according parameters as a string. You can copy the .env.default file, remove the .default suffix and edit it.
5. Flash the device by running `dm-flash` in your development shell. Then run
`run-main` to initially load all variables from the .env file onto the ESP32. Repeat this and the previous step for all ESP32s.
6. Connect your ESP32s to energy sources and place them with well over a meter of
space in between in a triangle shape.
7. Open another shell inside of the `./host` folder.
8. Again, run nix develop --extra-experimental-features nix-command --extra- ⌋
experimental-features flakes to open another development shell.
9. Run uv-run inside this console to startup the raw project inside of the command
line or run run-calibration to startup the calibration sequence.

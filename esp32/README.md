# Positional Tracking Client Side

This is the code that can get loaded onto an esp32.

### Open Tasks

1. We can implement a P0 (1m RSSI) and N (Path-loss exponent) calibration sequence. Right now, there are sane defaults for the esp32-c6-wroom-1 used - but to add other esps, it would be useful to have a sequence that calibrates the device. Maybe not on startup, but in a different command.

import binascii
import time

import aioble
import bluetooth
import config
import network
import uasyncio as asyncio

_BLE_SERVICE_UUID = bluetooth.UUID("19b10000-e8f2-537e-4f6c-d104768a1214")


target_UUIDs = ["d4:3a:2c:56:13:10"]

# Subject to be set by calibration sequence
P0 = -75.0  # RSSI measured exactly 1 meter away
N = 2.5  # Environmental path loss factor (2.0 = open, 3.0+ = heavy walls)


def rssi_to_distance(rssi):
    """Converts a filtered RSSI value into an approximate distance in meters."""
    try:
        return 10 ** ((P0 - rssi) / (10 * N))
    except Exception:
        return None


async def scan():
    print("Start Scan:")
    async with aioble.scan(
        duration_ms=0, interval_us=30000, window_us=30000, active=True
    ) as scanner:
        async for result in scanner:
            device_address = binascii.hexlify(result.device.addr, ":").decode("utf-8")

            for target_UUID in target_UUIDs:
                if device_address == target_UUID:
                    print(
                        "Found device. RSSI:",
                        result.rssi,
                        "\nEstimated distance:",
                        rssi_to_distance(result.rssi),
                    )


def connect_wifi():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(config.WIFI_NAME, config.WIFI_PASSWORD)

    print("Connecting to wifi", config.WIFI_NAME)

    # Wait for connection
    timeout = 10
    while not station.isconnected() and timeout > 0:
        print("Timeout (try ", 10 - timeout, "/10)")
        time.sleep(1)
        timeout -= 1

    if station.isconnected():
        print("Connection successful")
        print(station.ifconfig())
        return True
    else:
        print("Connection failed. Timeout reached")
        return False


async def main():
    connect_wifi()


# Allows to cancel
# scan_task = asyncio.create_task(main())
# scan_task.cancel()

asyncio.run(main())

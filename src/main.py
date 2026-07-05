import binascii

import aioble
import bluetooth
import uasyncio as asyncio

_BLE_SERVICE_UUID = bluetooth.UUID("19b10000-e8f2-537e-4f6c-d104768a1214")
# _BLE_SENSOR_CHAR_UUID = bluetooth.UUID('19b10001-e8f2-537e-4f6c-d104768a1214')
# _BLE_LED_UUID = bluetooth.UUID('19b10002-e8f2-537e-4f6c-d104768a1214')
# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000

target_UUIDs = ["d4:3a:2c:56:13:10"]

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
                        "\n Estimated distance:",
                        rssi_to_distance(result.rssi),
                    )

            # print(
            #     "Found device address",
            #     device_address,
            #     "with rssi of ",
            #     result.rssi,
            #     "and name",
            #     result.name(),
            # )


asyncio.run(scan())

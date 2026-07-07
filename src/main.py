import binascii
import time

import aioble
import bluetooth
import uasyncio as asyncio
from config import DEVICE_ID

_BLE_SERVICE_UUID = bluetooth.UUID("19b10000-e8f2-537e-4f6c-d104768a1214")
# _BLE_SENSOR_CHAR_UUID = bluetooth.UUID('19b10001-e8f2-537e-4f6c-d104768a1214')
# _BLE_LED_UUID = bluetooth.UUID('19b10002-e8f2-537e-4f6c-d104768a1214')
# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000

target_UUIDs = ["d4:3a:2c:56:13:10", "20:6e:f1:11:55:8e","94:45:60:37:F6:13", "20:6e:f1:11:66:b2"]  # S_Phone, ESP01, M_Phone, ESP02

P0 = -75.0  # RSSI measured exactly 1 meter away
N = 2.5  # Environmental path loss factor (2.0 = open, 3.0+ = heavy walls)

LOG_FILE = "rssi_log.csv"


def rssi_to_distance(rssi):
    """Converts a filtered RSSI value into an approximate distance in meters."""
    try:
        return 10 ** ((P0 - rssi) / (10 * N))
    except Exception:
        return None


def log_measurement(rssi, distance):
    line = "{},{},{},{}\n".format(DEVICE_ID, time.ticks_ms(), rssi, distance)
    with open(LOG_FILE, "a") as f:
        f.write(line)
    print(line, end="")

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
                    distance = rssi_to_distance(result.rssi)
                    log_measurement(result.rssi, distance)

            # print(
            #     "Found device address",
            #     device_address,
            #     "with rssi of ",
            #     result.rssi,
            #     "and name",
            #     result.name(),
            # )


async def advertise():
    while True:
        print("Advertising:", DEVICE_ID)
        await aioble.advertise(
            _ADV_INTERVAL_MS,
            name=DEVICE_ID,
            services=[_BLE_SERVICE_UUID],
        )

async def main():
    await asyncio.gather(scan(), advertise())

asyncio.run(main())

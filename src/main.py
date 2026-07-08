import asyncio
import json
import random
import time

import config
import network
from microdot import Microdot

import bluetooth
from Bluetooth import BluetoothScanner

# # Micropython does not use these import, so we just ignore. Types are stripped away anyway.
# try:
#     from typing import Callable, List
# except ImportError:
#     pass


def generate_nanoid(length=21):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_- "
    return "".join(random.choice(alphabet) for _ in range(0, length))


_BLE_SERVICE_UUID = bluetooth.UUID("19b10000-e8f2-537e-4f6c-d104768a1214")
ble = bluetooth.BLE()
ble.active(True)
_, mac_bytes = ble.config("mac")
DEVICE_MAC_ADDRESS = ":".join(f"{b:02X}" for b in mac_bytes)
app = Microdot()

_DEVICE_ID = generate_nanoid()


@app.route("/wake-up")
async def wake_up(request):
    """
    This api call is done to wake up this device. A similar one, to update a device that is already woken up can be found here [NOT YET IMPLEMENTED].

    This expects to get the identifier of the device that should be tracked, and, optionally, a bluetooth mac address.
    In turn, it sends the own identifier (that is dynamically generated) and a bluetooth mac address.
    """

    print("Whom woken up the ancient one?")

    # i guess we also need other identifiers?
    return json.dumps({"deviceId": _DEVICE_ID, "bluetoothMac": DEVICE_MAC_ADDRESS})


TARGET_BLUETOOTH_MACs = ["d4:3a:2c:56:13:10"]


def connect_wifi():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(config.WIFI_NAME, config.WIFI_PASSWORD)

    print("Connecting to wifi", config.WIFI_NAME)

    # Wait for connection
    timeout = 10
    while not station.isconnected() and timeout > 0:
        print("Timeout (try", 9 - timeout, "/ 10)")
        time.sleep(1)
        timeout -= 1

    if station.isconnected():
        print(f"connected to ${station.ifconfig()}")

        return True
    else:
        print("Connection failed. Timeout reached")
        return False


# TODO: Setup https. Not sure if it matters, but we may send confidential data. Better safe than sorry, but not in MVP.
async def setup_api_calls():
    print("Microdot server started on port 80")
    await app.start_server(port=80)


async def main():
    connect_wifi()

    # Wait for api calls to update.
    asyncio.create_task(setup_api_calls())

    # Setup bluetooth scanning
    other_esp_scanner = BluetoothScanner(TARGET_BLUETOOTH_MACs)

    def handleScanResult(id, rssi):
        print(f"found result ${id} with rsso ${rssi}")

    asyncio.create_task(other_esp_scanner.scan(handleScanResult, True))

    # Keep application alive indefinetely
    while True:
        await asyncio.sleep(1)


# Allows to cancel
# scan_task = asyncio.create_task(main())
# scan_task.cancel()

asyncio.run(main())

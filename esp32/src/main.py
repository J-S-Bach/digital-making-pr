import asyncio
import json
import random

from microdot import Microdot

import bluetooth
from Bluetooth import BluetoothScanner
from connect_wifi import connect_wifi

# # Micropython does not use these import, so we just ignore. Types are stripped away anyway.
# try:
#     from typing import Callable, List
# except ImportError:
#     pass


def generate_nanoid(length=21):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_- "
    return "".join(random.choice(alphabet) for _ in range(0, length))


ble = bluetooth.BLE()
ble.active(True)
_, mac_bytes = ble.config("mac")

DEVICE_MAC_ADDRESS = ":".join(f"{b:02X}" for b in mac_bytes)

app = Microdot()

_DEVICE_ID = generate_nanoid()


# Outdated due to mDNS discovery?
@app.route("/identify")
async def identify(request):
    """
    This api call is used to initially fetch data from this esp. With this, the host only needs to know the target ip address and we could even implement something elegant like mDNS?
    It does not expect any incoming parameter and sends own identifier (that is dynamically generated) and a bluetooth mac address.
    """

    # i guess we also need other identifiers?
    return json.dumps({"deviceId": _DEVICE_ID, "bluetoothMac": DEVICE_MAC_ADDRESS})


@app.route("/bluetooth/wake-up")
async def bluetooth_wake_up(request):
    """
    URL: `/bluetooth/wake-up`

    This api call is done to wake up this device.
    To update a device that is already woken, call `/bluetooth/switch-goal`.
    To power off bluetooth, call `/bluetooth/sleep`.

    This expects to get the IP address of the device it should send the udp packages to, and, optionally, a bluetooth mac address.
    `{
    "trackedDeviceMac": String
    "hostIP": String
    }`
    In turn, it starts streaming udp packages to the target ip address.
    """

    print("Whom woken up the ancient one?")

    return None

@app.route("/bluetooth/sleep")
async def bluetooth_sleep(request):
    """
    URL: `/bluetooth/sleep`

    This api call is done to power down bluetooth tracking.
    To power on bluetooth, call `/bluetooth/wake-up`.

    This call expects nothing, and returns nothing.
    """

    print("Whom woken up the ancient one?")

    return None

@app.route("/bluetooth/change")
async def bluetooth_change(request):
    """
    URL: `/bluetooth/change`

    This api call is used to update the current bluetooth tracking target.
    To power on bluetooth, call `/bluetooth/wake-up`.
    To power off bluetooth, call `/bluetooth/sleep`.


    """

    print("Whom changed the ancient one?")

    return None


TARGET_BLUETOOTH_UUIDs = [bluetooth.UUID(0xAAAA)]


# TODO: Setup https. Not sure if it matters, but we may send confidential data. Better safe than sorry, but not in MVP.
async def setup_api_calls():
    await app.start_server(port=80)


async def main():
    connect_wifi()

    # Wait for api calls to update.
    asyncio.create_task(setup_api_calls())

    # Setup bluetooth scanning
    other_esp_scanner = BluetoothScanner(TARGET_BLUETOOTH_UUIDs)

    def handleScanResult(id, rssi):
        print(f"found result ${id} with rsso ${rssi}")

    other_esp_scanner.subscribe(handleScanResult)
    asyncio.create_task(other_esp_scanner.start())


    # Keep application alive indefinetely
    while True:
        await asyncio.sleep(1)


# Allows to cancel
# scan_task = asyncio.create_task(main())
# scan_task.cancel()

asyncio.run(main())

import asyncio
import json
import random

from microdot import Microdot, Request

import bluetooth
from Bluetooth import BluetoothScanner
from connect_wifi import connect_wifi
from send_udp import send_udp_package

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
hostname = f"esp32-{DEVICE_MAC_ADDRESS[-6:]}"


# Outdated due to mDNS discovery?
@app.route("/identify", methods=["GET"])
async def identify(request: Request):
    """
    This api call is used to initially fetch data from this esp. With this, the host only needs to know the target ip address and we could even implement something elegant like mDNS?
    It does not expect any incoming parameter and sends own identifier (that is dynamically generated) and a bluetooth mac address.
    """

    # i guess we also need other identifiers?
    return json.dumps(
        {
            "deviceId": _DEVICE_ID,
            "hostname": hostname,
            "bluetoothMac": DEVICE_MAC_ADDRESS,
        }
    )


@app.route("/calibrate", methods=["POST"])
async def calibrate(request: Request):
    """
    This API call tries to fetch the position of the other esp devices to allow an estimation of relative positions of each device.

    Expects data of all other esp devices.
    Returns estimated position data.
    """

    # Setup bluetooth scanning: Switch target bluetooth UUIDs to the mac adresses of the other esps. We need to be able to switch between mac address and UUID or send an own UUID per device.
    other_esp_scanner = BluetoothScanner(TARGET_BLUETOOTH_UUIDs)

    def handleScanResult(id, rssi, distance):
        print(f"Found result ${id} with rsso ${rssi}")

    other_esp_scanner.subscribe(handleScanResult)
    asyncio.create_task(other_esp_scanner.start())


current_bluetooth_scanner: BluetoothScanner | None = None


# Is it useful to create a "shared" directory or custom package containing classes that define api calls and responses?
# TODO: For release: Input sanitizing
@app.route("/bluetooth/wake-up", methods=["POST"])
async def bluetooth_wake_up(request: Request):
    """
    URL: `/bluetooth/wake-up`

    This api call is done to wake up this device.
    To update a device that is already woken, call `/bluetooth/switch-goal`.
    To power off bluetooth, call `/bluetooth/sleep`.

    This expects to get the IP address of the device it should send the udp packages to, and a trackedServiceSSID in th 0xaaaa (16-bit integer) representation, encoded as a string.
    `{
    "trackedServiceSSID": String
    "host_address": String
    }`
    In turn, it starts streaming udp packages to the target ip address.
    """

    # Setup bluetooth scanning

    try:
        body_string: bytes = request.body.decode()  # type: ignore

        body = json.loads(body_string)

    except Exception as e:
        print(f"An error occurred during /bluetooth/wake-up: {e}")
        return 500

    encoded_uuid = int(body["trackedServiceSSID"], 16)

    device_bluetooth_scanner = BluetoothScanner([bluetooth.UUID(encoded_uuid)])

    def handle_bluetooth_device_discovery(
        uuid: bluetooth.UUID, rssi: int, estimated_distance: float
    ):
        send_udp_package(
            body["host_address"],
            json_obj={
                "technology": "BLUETOOTH",
                "deviceId": _DEVICE_ID,
                "estimatedDistance": estimated_distance,
            },
        )

    device_bluetooth_scanner.subscribe(handle_bluetooth_device_discovery)
    asyncio.create_task(device_bluetooth_scanner.start())

    return 200


@app.route("/bluetooth/sleep", methods=["POST"])
async def bluetooth_sleep(request: Request):
    """
    URL: `/bluetooth/sleep`

    This api call is done to power down bluetooth tracking.
    To power on bluetooth, call `/bluetooth/wake-up`.

    This call expects nothing, and returns nothing.
    """

    if current_bluetooth_scanner is not None:
        await current_bluetooth_scanner.pause()

    return 200


@app.route("/bluetooth/change", methods=["POST"])
async def bluetooth_change(request: Request):
    """
    URL: `/bluetooth/change`

    This api call is used to update the current bluetooth tracking target.
    To power on bluetooth, call `/bluetooth/wake-up`.
    To power off bluetooth, call `/bluetooth/sleep`.


    """

    print("Whom changed the ancient one?")

    return 200


TARGET_BLUETOOTH_UUIDs = [bluetooth.UUID(0xAAAA)]


# TODO: Setup https. Not sure if it matters, but we may send confidential data. Better safe than sorry, but not in MVP.
async def setup_api_calls():
    print("Started api server under port 80.")
    await app.start_server(port=80)


async def main():
    connected = connect_wifi(_DEVICE_ID, hostname)

    if not connected:
        raise Exception("Could not connect to wifi!")

    # Wait for api calls to update.
    asyncio.create_task(setup_api_calls())

    # Keep application alive indefinetely
    while True:
        await asyncio.sleep(1)


# Allows to cancel
# scan_task = asyncio.create_task(main())
# scan_task.cancel()

asyncio.run(main())

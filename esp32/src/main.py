import asyncio
import json
import random

import bluetooth
from microdot import Microdot, Request

from connect_wifi import connect_wifi
from esp32_bluetooth.Advertiser import BluetoothAdvertiser
from esp32_bluetooth.Scanner import BluetoothScanner
from send_udp import send_udp_package


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
bluetooth_advertiser = BluetoothAdvertiser()


@app.route("/bluetooth-visibility/enable", methods=["POST"])
async def bluetooth_visibility_enable(request: Request):

    await bluetooth_advertiser.start_advertising()

    return "Success", 200


@app.route("/bluetooth-visibility/disable", methods=["POST"])
async def bluetooth_visibility_disable(request: Request):
    await bluetooth_advertiser.stop_advertising()

    return "Success", 200


class CalibrationResult:
    def __init__(
        self, device_bluetooth_mac: str, estimated_distances: list[float]
    ) -> None:
        self.device_bluetooth_mac = device_bluetooth_mac
        self.estimated_distances = estimated_distances

    device_bluetooth_mac: str
    estimated_distances: list[float]


@app.route("/calibrate", methods=["POST"])
async def calibrate(request: Request):
    """
    This API call tries to fetch the position of the other esp devices to allow an estimation of relative positions of each device. Expects other devices not to move during calibration.

    Expects data of all other esp devices:
        {
            otherDeviceMacIds: [str]
        }
    Returns array of measurements:
        [
            {device_bluetooth_mac: str, estimated_distances: [float]}
        ]
    """

    try:
        body_string: bytes = request.body.decode()  # type: ignore
        body = json.loads(body_string)

    except Exception as e:
        print(f"An error occurred during /bluetooth/wake-up: {e}")
        return 500

    print(f"Got calibration request for {body['otherDeviceMacIds']}")
    # Setup bluetooth scanning: Switch target bluetooth UUIDs to the mac adresses of the other esps. We need to be able to switch between mac address and UUID or send an own UUID per device.
    other_device_scanner = BluetoothScanner(
        [],
        body["otherDeviceMacIds"],
    )

    # [{"device_bluetooth_mac": str, "estimated_distances": [float]}]
    results = [
        CalibrationResult(device_bluetooth_mac=bluetooth_mac_id, estimated_distances=[])
        for bluetooth_mac_id in body["otherDeviceMacIds"]
    ]

    def handleScanResult(id, rssi, distance):
        print(f"Found result {id} with rssi {rssi}")

        for result in results:
            print(result.device_bluetooth_mac.lower(), id.lower())
            if result.device_bluetooth_mac.lower() == id.lower():
                result.estimated_distances.append(distance)
            else:
                raise Exception("Found distance for unkown bluetooth mac")

        individual_device_found_distances_list_length = [
            len(result.estimated_distances) for result in results
        ]

        are_all_devices_found_more_than_10_times = all(
            x <= 10 for x in individual_device_found_distances_list_length
        )

        # TODO: Also set a timeout if one other device is not reachable!
        if are_all_devices_found_more_than_10_times:

            async def do_cancel():
                print("Ending scanning for calibration sequence...")
                scanning_task.cancel()

            asyncio.create_task(
                do_cancel()
            )  # this schedules cancellation outside of this event loop.

    other_device_scanner.subscribe(handleScanResult)

    scanning_task = asyncio.create_task(other_device_scanner.start())

    await scanning_task

    print(f"Sending {results}")

    return 200, results


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
    global current_bluetooth_scanner

    # Setup bluetooth scanning

    try:
        body_string: bytes = request.body.decode()  # type: ignore
        body = json.loads(body_string)

    except Exception as e:
        print(f"An error occurred during /bluetooth/wake-up: {e}")
        return 500

    if current_bluetooth_scanner is not None:
        return 204

    encoded_uuid = int(body["trackedServiceSSID"], 16)

    current_bluetooth_scanner = BluetoothScanner([bluetooth.UUID(encoded_uuid)])

    def handle_bluetooth_device_discovery(
        uuid: bluetooth.UUID | str, rssi: int, estimated_distance: float
    ):
        send_udp_package(
            body["host_address"],
            json_obj={
                "technology": "BLUETOOTH",
                "deviceId": _DEVICE_ID,
                "estimatedDistance": estimated_distance,
            },
        )

    current_bluetooth_scanner.subscribe(handle_bluetooth_device_discovery)
    asyncio.create_task(current_bluetooth_scanner.start())
    return 200


@app.route("/bluetooth/sleep", methods=["POST"])
async def bluetooth_sleep(request: Request):
    """
    URL: `/bluetooth/sleep`

    This api call is done to power down bluetooth tracking.
    To power on bluetooth, call `/bluetooth/wake-up`.

    This call expects nothing, and returns nothing.
    """
    global current_bluetooth_scanner

    if current_bluetooth_scanner is not None:
        await current_bluetooth_scanner.pause()
        current_bluetooth_scanner = None

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


asyncio.run(main())

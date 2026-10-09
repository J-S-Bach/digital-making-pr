import atexit
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import NamedTuple

import requests

from src.discover_clients import DeviceData


# ADD POSSIBLE NEW TECHNOLOGIES HERE TO RECEIVE THEM! REGISTER THEM INTO THE EXISTING SUBSCRIPTIONS TO ALLOW FURTHER PROCESSING.
class PeerDistanceMeasurement(NamedTuple):
    target_device: DeviceData
    distances: list[float]


class NodeCalibrationData(NamedTuple):
    source_device: DeviceData
    peer_measurements: list[PeerDistanceMeasurement]


class TechnologyHandler:
    """
    Is able to activate and shutdown technologies.
    """

    def __init__(
        self, tracking_devices: list[DeviceData], target_udp_address: str
    ) -> None:
        self.tracking_devices: list[DeviceData] = tracking_devices
        self.target_udp_address: str = target_udp_address
        _ = atexit.register(self.disable_bluetooth)

    def _post_for_all_devices(self, path: str):
        def fetch(url: str):
            response = requests.post(url)
            response.raise_for_status()

        urls = [
            ("http://" + device.ip_address + path) for device in self.tracking_devices
        ]

        try:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(fetch, url) for url in urls]

                response = [future.result() for future in as_completed(futures)]
                print(f"Sent POST to: All devices | {path}")
                return response
        except requests.exceptions.RequestException as e:
            print(f"Operation failed: {e}")

    def activate_all_device_visibility(self):
        _ = self._post_for_all_devices("/bluetooth-visibility/enable")

    def deactivate_all_device_visibility(self):
        _ = self._post_for_all_devices("/bluetooth-visibility/disable")

    def scan_device_positions(self):
        if (
            len(self.tracking_devices) > 1
            and not "--no-calibration" in sys.argv
            and not "-g" in sys.argv
        ):
            self.activate_all_device_visibility()
            clients_positions_estimations: list[NodeCalibrationData] = []

            for device in self.tracking_devices:
                other_devices = filter(
                    lambda device_to_track: device_to_track is not device,
                    self.tracking_devices,
                )

                other_bluetooth_macs = [
                    device.bluetooth_mac for device in other_devices
                ]
                print(f"Sending calibration command to {device.hostname}...")

                response = requests.post(
                    "http://" + device.ip_address + "/other-client-positions",
                    json={"otherDeviceMacIds": other_bluetooth_macs},
                )

                response.raise_for_status()

                print(f"Got Response of {response.json()}")

                other_devices_distances = [
                    PeerDistanceMeasurement(
                        target_device=next(
                            dev
                            for dev in self.tracking_devices
                            if dev.bluetooth_mac
                            == json_response["device_bluetooth_mac"]
                        ),
                        distances=json_response["estimated_distances"],
                    )
                    for json_response in response.json()
                ]

                clients_positions_estimations.append(
                    NodeCalibrationData(
                        source_device=device,
                        peer_measurements=other_devices_distances,
                    )
                )

            self.deactivate_all_device_visibility()

            return clients_positions_estimations

    def activate_bluetooth(self):
        for device in self.tracking_devices:
            try:
                # Yeah this should be abstracted to something prettier. Maybe https?

                print("Activating Bluetooth...")
                _ = requests.post(
                    "http://" + device.ip_address + "/bluetooth/wake-up",
                    json={
                        "trackedServiceSSID": "0xAAAA",
                        "host_address": self.target_udp_address,
                    },
                )

            except ConnectionError as e:
                print(f"Unable to connect to {device.hostname} due to {e}")

    def disable_bluetooth(self):
        for device in self.tracking_devices:
            try:
                # Yeah this should be abstracted to something prettier. Maybe https?

                print("Disabling Bluetooth...")
                _ = requests.post(
                    "http://" + device.ip_address + "/bluetooth/sleep",
                )

            except ConnectionError as e:
                print(f"Unable to connect to {device.hostname} due to {e}")

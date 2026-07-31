import atexit
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from src.discover_clients import DeviceData

# ADD POSSIBLE NEW TECHNOLOGIES HERE TO RECEIVE THEM! REGISTER THEM INTO THE EXISTING SUBSCRIPTIONS TO ALLOW FURTHER PROCESSING.


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
            ("http://" + device["ip_address"] + path)
            for device in self.tracking_devices
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

    def calibrate_device_positions(self):
        if len(self.tracking_devices) > 1:
            self.activate_all_device_visibility()

            for device in self.tracking_devices:
                other_devices = filter(lambda x: True, self.tracking_devices)

                other_bluetooth_macs = [
                    device["bluetooth_mac"] for device in other_devices
                ]
                print(f"Sending calibration command to {device['hostname']}")
                # TODO: Return posts
                _ = requests.post(
                    "http://" + device["ip_address"] + "/calibrate",
                    json={"otherDeviceMacIds": other_bluetooth_macs},
                )

            self.deactivate_all_device_visibility()

    def activate_bluetooth(self):
        for device in self.tracking_devices:
            try:
                # Yeah this should be abstracted to something prettier. Maybe https?

                print("Activating Bluetooth...")
                _ = requests.post(
                    "http://" + device["ip_address"] + "/bluetooth/wake-up",
                    json={
                        "trackedServiceSSID": "0xAAAA",
                        "host_address": self.target_udp_address,
                    },
                )

            except Exception as e:
                print(f"Unable to connect to {device['hostname']} due to {e}")

    def disable_bluetooth(self):
        for device in self.tracking_devices:
            try:
                # Yeah this should be abstracted to something prettier. Maybe https?

                print("Disabling Bluetooth...")
                _ = requests.post(
                    "http://" + device["ip_address"] + "/bluetooth/sleep",
                )

            except Exception as e:
                print(f"Unable to connect to {device['hostname']} due to {e}")

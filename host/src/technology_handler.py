import json

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

import json
import os
import socket
from dataclasses import dataclass

from dotenv import load_dotenv

from src.self_identification import get_own_ip


@dataclass
class DeviceData:
    hostname: str
    ip_address: str
    bluetooth_mac: str
    device_id: str


_ = load_dotenv()

MULTICAST_GROUP = "224.0.0.251"
DISCOVERY_PORT = int(os.getenv("DISCOVERY_PORT") or 6767)


def discover_clients():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.settimeout(2.0)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    local_ip = get_own_ip()
    print(f"Sending discovery request to all ESP32s (from {local_ip})...")

    sock.bind(("", DISCOVERY_PORT))

    try:
        sock.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_MULTICAST_IF,
            socket.inet_aton(local_ip),
        )
    except OSError:
        pass

    sock.sendto(b"_esp32-tracker-discovery-service", (MULTICAST_GROUP, DISCOVERY_PORT))

    devices: list[DeviceData] = []
    try:
        while True:
            data, _ = sock.recvfrom(1024)
            msg = data.decode()
            if msg.startswith("ESP32-TRACKER-DISCOVERY-RESPONSE:"):
                _, json_object = msg.split(":", 1)
                res = json.loads(json_object)
                devices.append(
                    DeviceData(
                        hostname=res["hostname"],
                        ip_address=res["ipAddress"],
                        bluetooth_mac=res["bluetoothMac"],
                        device_id=res["deviceId"],
                    )
                )
    except TimeoutError:
        print(f"Discovery finished. Found {len(devices)} devices:")
        for device in devices:
            print(
                f"  - Name: {device.hostname} | IP: {device.ip_address} | Bluetooth Mac: {device.bluetooth_mac} | Identifier: {device.device_id}"
            )

    return devices

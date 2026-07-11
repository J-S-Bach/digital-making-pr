import json
import os
import socket
from dotenv import load_dotenv
from typing import Required, TypedDict

class DeviceData(TypedDict, total=False):
    hostname: Required[str]
    ipAddress: Required[str]
    bluetoothMac: Required[str]

_ = load_dotenv()

MULTICAST_GROUP = '224.0.0.251'
DISCOVERY_PORT = os.getenv('DISCOVERY_PORT') or 6767

def discover_clients():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)


    print("Sending discovery request to all ESP32s...")
    _ = sock.sendto(b'_esp32-tracker-discovery-service', (MULTICAST_GROUP, DISCOVERY_PORT))

    devices: list[DeviceData] = []
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            msg = data.decode()
            if msg.startswith("ESP32-TRACKER-DISCOVERY-RESPONSE:"):
                _, json_object = msg.split(":", 1)
                res = json.loads(json_object)
                devices.append({"hostname": res["hostname"], "ipAddress": res["ipAddress"], "bluetoothMac": res["bluetoothMac"]})
    except socket.timeout:
        print(f"Discovery finished. Found {len(devices)} devices:")
        for device in devices:
            print(f"  - Name: {device['hostname']} | IP: {device['ipAddress']} | Bluetooth Mac: {device['bluetoothMac']}")


    return devices

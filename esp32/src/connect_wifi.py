import asyncio
import json
import select
import socket
import struct
import time

import bluetooth
import config
import network

ble = bluetooth.BLE()
ble.active(True)
_, mac_bytes = ble.config("mac")
DEVICE_MAC_ADDRESS = ":".join(f"{b:02X}" for b in mac_bytes)


def connect_wifi(device_id: str, hostname: str):
    station = network.WLAN(network.STA_IF)
    network.hostname(hostname)

    station.active(True)
    station.connect(config.WIFI_NAME, config.WIFI_PASSWORD)

    print(f'Trying to Connecting to wifi "{config.WIFI_NAME}"...')

    # Wait for connection
    timeout = 10
    while not station.isconnected() and timeout > 0:
        print("Timeout (try", 11 - timeout, "/ 10)")
        time.sleep(1)
        timeout -= 1

    if station.isconnected():
        ip = station.ifconfig()[0]
        asyncio.create_task(start_mdns_responder(hostname, device_id, ip))
        print(f"Connected as {hostname}.local under IP address {station.ifconfig()[0]}")

        return True
    else:
        print("Connection failed. Timeout reached")
        return False


def inet_aton(ip_str):
    return bytes(map(int, ip_str.split(".")))


# This function is partially AI generated (Gemini).
async def start_mdns_responder(hostname: str, device_id: str, ip_address):
    """
    Listens for UDP multicast queries on the network and responds
    if a host is looking for _esp32-tracker-discovery-service.
    """

    # Standard mDNS multicast group and port
    MDNS_ADDR = "224.0.0.251"
    MDNS_PORT = getattr(config, "DISCOVERY_PORT", 6767)

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", MDNS_PORT))
    sock.setblocking(False)

    # Join the multicast group
    mreq = struct.pack("4s4s", inet_aton(MDNS_ADDR), inet_aton("0.0.0.0"))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(
        "mDNS Service Discovery active... Listening for '_esp32-tracker-discovery-service'"
    )

    poller = select.poll()
    poller.register(sock, select.POLLIN)

    while True:
        try:
            # Check if data is ready without blocking the loop
            if poller.poll(0):  # 0 ms timeout = instant check
                data, addr = sock.recvfrom(1024)
                if b"_esp32-tracker-discovery-service" in data:
                    response = "ESP32-TRACKER-DISCOVERY-RESPONSE:" + json.dumps(
                        {
                            "hostname": hostname,
                            "deviceId": device_id,
                            "ipAddress": ip_address,
                            "bluetoothMac": DEVICE_MAC_ADDRESS,
                        }
                    )
                    sock.sendto(response.encode(), addr)

            # Yield control back to asyncio loop to let Bluetooth run
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"mDNS exception: {e}")

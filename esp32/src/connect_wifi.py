import asyncio
import json

import bluetooth
import config
import network
import time
import ubinascii
import socket
import struct

ble = bluetooth.BLE()
ble.active(True)
_, mac_bytes = ble.config("mac")
DEVICE_MAC_ADDRESS = ":".join(f"{b:02X}" for b in mac_bytes)


def connect_wifi():
    station = network.WLAN(network.STA_IF)

    wifi_mac = ubinascii.hexlify(station.config('mac')).decode()
    hostname = f"esp32-{wifi_mac[-6:]}"
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
        asyncio.create_task(start_mdns_responder(hostname, ip))
        print(f"Connected as {hostname}.local under IP address {station.ifconfig()[0]}")

        return True
    else:
        print("Connection failed. Timeout reached")
        return False


def inet_aton(ip_str):
    return bytes(map(int, ip_str.split('.')))

# This function is partially AI generated (Gemini).
async def start_mdns_responder(hostname, ip_address):
    """
    Listens for UDP multicast queries on the network and responds
    if a host is looking for _esp32-tracker-discovery-service.
    """

    # Standard mDNS multicast group and port
    MDNS_ADDR = '224.0.0.251'
    MDNS_PORT = 12345

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MDNS_PORT))

    # Join the multicast group
    mreq = struct.pack('4s4s', inet_aton(MDNS_ADDR), inet_aton('0.0.0.0'))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print("mDNS Service Discovery active... Listening for '_esp32-tracker-discovery-service'")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            print(f"data {data} {addr}")
            # Check if the incoming request contains our custom service type string
            if b'_esp32-tracker-discovery-service' in data:
                # Send a simple target payload response back to the laptop
                # In a production environment, you'd format a real DNS response,
                # but a direct UDP reply back to the sender works beautifully for custom tools.
                response = "ESP32-TRACKER-DISCOVERY-RESPONSE:" + json.dumps({"hostname": hostname, "ipAddress": ip_address, "bluetoothMac": DEVICE_MAC_ADDRESS})
                sock.sendto(response.encode(), addr)
        except Exception as e:
            print("mDNS Error:", e)

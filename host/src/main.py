import json
import socket

MULTICAST_GROUP = '224.0.0.251'
PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2.0)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)


print("Sending discovery request to all ESP32s...")
sock.sendto(b'_esp32-tracker-discovery-service', (MULTICAST_GROUP, PORT))

devices = []
try:
    while True:
        data, addr = sock.recvfrom(1024)
        msg = data.decode()
        if msg.startswith("ESP32-TRACKER-DISCOVERY-RESPONSE:"):
            _, json_object = msg.split(":", 1)
            res = json.loads(json_object)
            devices.append({"hostname": res["hostname"], "ip": res["ipAddress"], "bluetoothMac": res["bluetoothMac"]})
except socket.timeout:
    print("Discovery finished.")

print("\n--- Found Devices ---")
for dev in devices:
    print(f"Hostname: {dev['hostname']}.local | IP Address: {dev['ip']} | bluetoothMac: {dev['bluetoothMac']}")

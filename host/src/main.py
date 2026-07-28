import socket
from .discover_clients import discover_clients
import requests

devices = discover_clients()

UDP_PORT = 6969

for device in devices:
    try:

        # Yeah this should be abstracted to something prettier. Maybe https? and also, disocver ip better.
        local_hostname = socket.gethostname()
        ip_addresses = socket.gethostbyname_ex(local_hostname)[2]
        filtered_ips = [ip for ip in ip_addresses if not ip.startswith("127.")]
        first_ip = filtered_ips[:1]

        response = requests.post("http://" + device['ipAddress'] + "/bluetooth/wake-up", json={"trackedServiceSSID": "0xAAAA", "host_address": f"http://{first_ip[0]}:{UDP_PORT}"})

    except Exception as e:
        print(f"Unable to connect to {device['hostname']} due to {e}")


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind(("0.0.0.0", UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024)
    print("received message: %s" % data)

import json
import socket


def send_udp_package(target_address: str, json_obj: dict[str, str | int | float]):
    try:
        json_str = json.dumps(json_obj)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host, port = target_address.replace("http://", "").split(":")

        sock.sendto(json_str.encode(), (host, int(port)))

        print(f"Sent {json_str} to {target_address}.")
    except Exception as e:
        print(f"Error while sending udp package to {target_address}: {e}")

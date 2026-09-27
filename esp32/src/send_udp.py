import gc
import json
import socket


class TECHNOLOGY:
    BLUETOOTH = "BLUETOOTH"


# Global persistent socket
_udp_sock = None


def _get_udp_socket():
    global _udp_sock
    if _udp_sock is None:
        _udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return _udp_sock


def send_udp_package(target_address: str, json_obj: dict[str, str | int | float]):
    try:
        gc.collect()

        json_str = json.dumps(json_obj)
        host, port = target_address.replace("http://", "").split(":")

        sock = _get_udp_socket()
        sock.sendto(json_str.encode(), (host, int(port)))

        print(f"Sent {json_str} to {target_address}.")
    except Exception as e:
        print(f"Error while sending udp package to {target_address}: {e}")

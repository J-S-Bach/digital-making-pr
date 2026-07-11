from .discover_clients import discover_clients
import requests

devices = discover_clients()

for device in devices:
    try:
        response = requests.get("http://" + device['ipAddress'] + "/bluetooth/wake-up")
        print(response)
    except Exception as e:
        print(f"Unable to connect to {device['hostname']} due to {e}")

import config
import network
import time
import ubinascii


def connect_wifi():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(config.WIFI_NAME, config.WIFI_PASSWORD)

    print(f'Trying to Connecting to wifi "{config.WIFI_NAME}"...')

    wifi_mac = ubinascii.hexlify(station.config('mac')).decode()
    hostname = f"esp32-{wifi_mac[-6:]}"
    network.hostname(hostname)

    # Wait for connection
    timeout = 10
    while not station.isconnected() and timeout > 0:
        print("Timeout (try", 9 - timeout, "/ 10)")
        time.sleep(1)
        timeout -= 1

    if station.isconnected():

        print(f"Connected as {hostname}.local under IP address {station.ifconfig()[0]}")

        return True
    else:
        print("Connection failed. Timeout reached")
        return False

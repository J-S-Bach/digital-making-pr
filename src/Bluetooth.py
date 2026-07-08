import aioble

try:
    from typing import Callable, List
except ImportError:
    pass


class BluetoothScanner:
    search_macs: List[str] = []

    # Subject to be set by calibration sequence - therefore updatable by __init__
    P0 = -75.0
    """
    RSSI measured exactly 1 meter away
    """
    N = 2.5
    """
    Environmental path loss factor (2.0 = open, 3.0+ = heavy walls)
    """

    def __init__(
        self, search_macs: List[str], P0: int | None = None, N: int | None = None
    ) -> None:
        self.search_macs = search_macs

        if P0 is not None:
            self.P0 = P0

        if N is not None:
            self.N = N

    # TODO: If you have too much time and motivation: Type onResultFound's first parameter to be of the type of the static ids given in the __init__
    async def scan(
        self,
        onResultFound: Callable[[str, int], None],
        continuously: bool | None = False,
    ):
        """
        Start a scan with the given ids (construction parameters).

        `onResultFound` is called either once per found id (if `continuously` is set to False) or multiple times per found id (if `continuously` is set to True).
        `continuously` has just been explained!
        """
        async with aioble.scan(
            duration_ms=0,
            interval_us=30000 if continuously else None,
            window_us=30000 if continuously else None,
            active=True,
        ) as scanner:
            print(f"Starting to scan for address(es) {', '.join(self.search_macs)}")
            async for result in scanner:
                device_bluetooth_mac = result.device.addr_hex()

                for target_bluetooth_mac in self.search_macs:
                    if device_bluetooth_mac == target_bluetooth_mac:
                        if result.rssi is None:
                            raise Exception(
                                f"No rssi provided from scan to ${device_bluetooth_mac}!"
                            )
                        print("result!")
                        onResultFound(target_bluetooth_mac, int(result.rssi))

    def _rssi_to_distance(self, rssi):
        """Converts a filtered RSSI value into an approximate distance in meters."""
        try:
            return 10 ** ((self.P0 - rssi) / (10 * self.N))
        except Exception:
            return None

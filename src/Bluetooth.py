import aioble
from aioble.central import scan

import bluetooth

try:
    from typing import Callable, List
except ImportError:
    pass


class BluetoothScanner:
    target_service_uuids: List[bluetooth.UUID] = []
    # Subject to be set by calibration sequence - therefore updatable by __init__
    P0 = -75.0
    """
    RSSI measured exactly 1 meter away
    """
    N = 2.5
    """
    Environmental path loss factor (2.0 = open, 3.0+ = heavy walls)
    """

    _active_scanner: scan | None = None
    _subscriptions: List[Callable[[bluetooth.UUID, int], None]] = []

    def __init__(
        self,
        search_macs: List[bluetooth.UUID],
        P0: int | None = None,
        N: int | None = None,
    ) -> None:
        self.target_service_uuids = search_macs

        if P0 is not None:
            self.P0 = P0

        if N is not None:
            self.N = N

    def subscribe(self, func: Callable[[bluetooth.UUID, int], None]):
        """
        Register a function here that should be called when a scan result has been found. If you want to only find a scan result once, use `unsubscribe` and / or `pause` to cancel it.
        """
        self._subscriptions.append(func)

    def unsubscribe(self, func: Callable[[bluetooth.UUID, int], None]):
        """
        You need to provide the same function to cancel it. Take care of it!
        """
        self._subscriptions.remove(func)

    async def start(self):
        """
        Call this function to start scanning. Initially is not scanning!
        """
        await self._scan()

    async def pause(self):
        """
        Call this function to pause. Initially is not scanning!
        """
        if self._active_scanner is not None:
            await self._active_scanner.cancel()

    def _call_subscriptions(self, mac: bluetooth.UUID, rssi: int):
        for subscription in self._subscriptions:
            subscription(mac, rssi)

    # TODO: If you have too much time and motivation: Type onResultFound's first parameter to be of the type of the static ids given in the __init__
    async def _scan(
        self,
        # onResultFound: Callable[[str, int], None],
        # continuously: bool | None = False,
    ):
        """
        Start a scan with the given ids (construction parameters).

        `onResultFound` is called either once per found id (if `continuously` is set to False) or multiple times per found id (if `continuously` is set to True).
        `continuously` has just been explained!
        """
        async with aioble.scan(
            duration_ms=0,
            interval_us=1280000,
            window_us=1280000,
            active=True,
        ) as scanner:
            uuid_strings = [str(uuid) for uuid in self.target_service_uuids]
            joined_uuids = ", ".join(uuid_strings)

            print(f"Starting to scan for address(es) {joined_uuids}")
            self._active_scanner = scanner

            async for result in scanner:
                for uuid in result.services():
                    for target_service_uuid in self.target_service_uuids:
                        if target_service_uuid == uuid:
                            if result.rssi is None:
                                raise Exception(
                                    f"No rssi provided from scan to ${target_service_uuid}!"
                                )
                            print("result!")
                            self._call_subscriptions(mac=uuid, rssi=int(result.rssi))

    def _rssi_to_distance(self, rssi):
        """Converts a filtered RSSI value into an approximate distance in meters."""
        try:
            return 10 ** ((self.P0 - rssi) / (10 * self.N))
        except Exception:
            return None

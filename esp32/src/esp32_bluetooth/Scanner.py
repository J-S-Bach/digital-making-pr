import aioble
import bluetooth
from aioble.central import scan

try:
    from collections.abc import Callable
except ImportError:
    pass


class BluetoothScanner:
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
        self,
        target_service_uuids: list[bluetooth.UUID] | None = None,
        target_bluetooth_macs: list[str] | None = None,
        P0: float | None = None,
        N: float | None = None,
    ) -> None:
        self._active_scanner: scan | None = None
        self._subscriptions: list[Callable[[bluetooth.UUID | str, int, float]]] = []

        self.target_service_uuids = (
            target_service_uuids if target_service_uuids is not None else []
        )
        self.target_bluetooth_macs = (
            target_bluetooth_macs if target_bluetooth_macs is not None else []
        )

        if P0 is not None:
            self.P0 = P0

        if N is not None:
            self.N = N

    def subscribe(self, func: Callable[[bluetooth.UUID | str, int, float]]):
        """
        Register a function here that should be called when a scan result has been found. If you want to only find a scan result once, use `unsubscribe` and / or `pause` to cancel it.
        """
        self._subscriptions.append(func)

    def unsubscribe(self, func: Callable[[bluetooth.UUID | str, int, float]]):
        """
        You need to provide the same function to cancel it. Take care of it!
        """
        self._subscriptions.remove(func)

    async def start(self):
        """
        Call this function to start scanning. Initially is not scanning!
        """
        print(
            f"Started Bluetooth scanning for uuids {', '.join(map(str, self.target_service_uuids))} and macs {', '.join(map(str, self.target_bluetooth_macs))} (P0:{self.P0} N:{self.N})"
        )
        await self._scan()

    async def pause(self):
        """
        Call this function to pause. Initially is not scanning!
        """
        print(
            f"Paused Bluetooth scanning for uuids {', '.join(map(str, self.target_service_uuids))}"
        )

        if self._active_scanner is not None:
            await self._active_scanner.cancel()

    def _call_subscriptions(self, mac: bluetooth.UUID | str, rssi: int):
        for subscription in self._subscriptions:
            subscription(mac, rssi, self._rssi_to_distance(rssi))

    # TODO: If you have too much time and motivation: Type onResultFound's first parameter to be of the type of the static ids given in the __init__
    async def _scan(
        self,
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
            self._active_scanner = scanner

            async for result in scanner:
                # check if matching mac address
                mac_hex = result.device.addr_hex()

                for target_bluetooth_mac in self.target_bluetooth_macs:
                    if mac_hex.lower() == target_bluetooth_mac.lower():
                        assert result.rssi is not None, "No rssi provided from scan!"

                        self._call_subscriptions(mac_hex, rssi=result.rssi)

                # OR if matching service id!
                for uuid in result.services():
                    for target_service_uuid in self.target_service_uuids:
                        if target_service_uuid == uuid:
                            if result.rssi is None:
                                assert result.rssi is not None, (
                                    "No rssi provided from scan!"
                                )

                            self._call_subscriptions(mac=uuid, rssi=int(result.rssi))

    def _rssi_to_distance(self, rssi: int) -> float:
        """Converts a filtered RSSI value into an approximate distance in meters."""
        return 10 ** ((self.P0 - rssi) / (10 * self.N))

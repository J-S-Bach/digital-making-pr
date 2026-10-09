import asyncio
import aioble
import bluetooth

class BluetoothAdvertiser:
    def __init__(self):
        self._advertiser_task = None

    async def start_advertising(self):
        if self._advertiser_task is None:
            self._advertiser_task = asyncio.create_task(self._advertise_loop())

    async def _advertise_loop(self):
        try:
            await aioble.advertise(100_000, name="esp32-", services=[])
        except asyncio.CancelledError:
            bluetooth.BLE().gap_advertise(None)
            raise

    async def stop_advertising(self):
        if self._advertiser_task is not None:
            self._advertiser_task.cancel()
            try:
                await self._advertiser_task
            except asyncio.CancelledError:
                pass
            self._advertiser_task = None


class BluetoothScanner:
    P0 = -75.0
    N = 2.5

    def __init__(self, target_service_uuids=None, target_bluetooth_macs=None, P0=None, N=None):
        self._scan_task = None
        self._subscriptions = []
        self.target_service_uuids = target_service_uuids or []
        self.target_bluetooth_macs = target_bluetooth_macs or []
        if P0 is not None: self.P0 = P0
        if N is not None: self.N = N

    def subscribe(self, func):
        self._subscriptions.append(func)

    def unsubscribe(self, func):
        self._subscriptions.remove(func)

    async def start(self):
        if self._scan_task is None:
            self._scan_task = asyncio.create_task(self._scan())

    async def pause(self):
        if self._scan_task is not None:
            self._scan_task.cancel()
            try:
                await self._scan_task
            except asyncio.CancelledError:
                pass
            self._scan_task = None

    def _call_subscriptions(self, mac, rssi):
        for sub in self._subscriptions:
            sub(mac, rssi, 10 ** ((self.P0 - rssi) / (10 * self.N)))

    async def _scan(self):
        try:
            async with aioble.scan(duration_ms=0, interval_us=1280000, window_us=1280000, active=True) as scanner:
                async for result in scanner:
                    mac_hex = result.device.addr_hex()
                    for target_mac in self.target_bluetooth_macs:
                        if mac_hex.lower() == target_mac.lower() and result.rssi is not None:
                            self._call_subscriptions(mac_hex, rssi=result.rssi)
                    for uuid in result.services():
                        for target_uuid in self.target_service_uuids:
                            if target_uuid == uuid and result.rssi is not None:
                                self._call_subscriptions(mac=uuid, rssi=int(result.rssi))
        except asyncio.CancelledError:
            raise

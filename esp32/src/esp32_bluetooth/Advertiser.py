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

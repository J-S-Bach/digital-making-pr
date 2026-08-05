import asyncio

import aioble


class BluetoothAdvertiser:
    async def start_advertising(self):
        print("Started bluetooth advertising with values...")
        self.advertiser = asyncio.create_task(
            aioble.advertise(
                100_000,
                name="esp32-",
                services=[],
            )
        )

    async def stop_advertising(self):
        print("Stopped bluetooth advertising...")
        if self.advertiser is not None:
            self.advertiser.cancel()
            self.advertiser = None

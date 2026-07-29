import asyncio
import json
import socket
from collections.abc import Callable
from enum import Enum


# Correct enum import from standard library
class TECHNOLOGY(Enum):
    BLUETOOTH = "BLUETOOTH"


type EstimatedDistance = float
type DeviceId = str
type IncomingDataSubscription = Callable[
    [TECHNOLOGY, EstimatedDistance, DeviceId], None
]


class IncomingDataHandler:
    def __init__(self, udp_port: int) -> None:
        self.udp_port: int = udp_port
        self.subscriptions: list[IncomingDataSubscription] = []
        self._task: asyncio.Task[None] | None = None

    def start(self) -> None:
        self._task = asyncio.ensure_future(self._start_scanning())

    def stop(self) -> None:
        if self._task is not None:
            _ = self._task.cancel()

    async def _start_scanning(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)  # Important for asyncio
        sock.bind(("0.0.0.0", self.udp_port))

        loop = asyncio.get_running_loop()

        try:
            while True:
                # Async read without blocking the event loop
                data, _ = await loop.sock_recvfrom(sock, 1024)
                received_data = json.loads(data.decode("utf-8"))

                self._call_subscriptions(
                    received_data["technology"],
                    received_data["estimatedDistance"],
                    received_data["deviceId"],
                )
        except Exception as e:
            print(f"Error receiving UDP packet: {e}")
        finally:
            sock.close()

    def subscribe(self, func: IncomingDataSubscription) -> None:
        self.subscriptions.append(func)

    def unsubscribe(self, func: IncomingDataSubscription) -> None:
        self.subscriptions.remove(func)

    def _call_subscriptions(
        self, technology: TECHNOLOGY, estimated: EstimatedDistance, device_id: DeviceId
    ) -> None:
        for subscription in self.subscriptions:
            subscription(technology, estimated, device_id)

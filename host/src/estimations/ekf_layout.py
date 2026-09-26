from abc import ABC, abstractmethod
from datetime import datetime
from typing import NamedTuple, Self

from src.discover_clients import DeviceData


class Position(NamedTuple):
    x: float
    y: float


class DevicePosition(DeviceData):
    def __init__(
        self,
        hostname: str,
        ip_address: str,
        bluetooth_mac: str,
        device_id: str,
        position: Position,
    ):
        self.position: Position = position
        super().__init__(hostname, ip_address, bluetooth_mac, device_id)

    @classmethod
    def from_DeviceData(cls, device_data: DeviceData, position: Position) -> Self:
        return cls(
            bluetooth_mac=device_data.bluetooth_mac,
            device_id=device_data.device_id,
            hostname=device_data.hostname,
            ip_address=device_data.ip_address,
            position=position,
        )


class EkfCorrection(NamedTuple):
    x: float
    vx: float
    y: float
    vy: float


class EkfLayout(ABC):
    @abstractmethod
    def __init__(
        self,
        scanner_locations: list[DevicePosition],
        base_noise_variance: float = 0.1,
    ):
        pass

    base_variance: float

    descriptor: str = "Not selected"

    @abstractmethod
    def add_measurement(
        self, scanner_id: str, distance: float, timestamp: datetime | float | None
    ):
        """Collects incoming measurements into a buffer over time."""

    @abstractmethod
    def get_state(self, timestamp: datetime | float | None) -> EkfCorrection:
        """Returns current estimated position and velocity."""

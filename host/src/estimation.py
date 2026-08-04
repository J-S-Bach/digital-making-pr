import time
from dataclasses import asdict
from typing import Any, NamedTuple, Self

import numpy as np
from filterpy.common import Q_discrete_white_noise
from filterpy.kalman import ExtendedKalmanFilter
from numpy.typing import NDArray

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


class LiveEKFTracker:
    def __init__(
        self,
        scanner_locations: list[DevicePosition],
        base_noise_variance: float = 0.5,
    ):

        self.scanners: dict[str, NDArray[Any]] = {
            scanner_location.device_id: np.array(
                [scanner_location.position.x, scanner_location.position.y]
            )
            for scanner_location in scanner_locations
        }
        self.base_variance: float = base_noise_variance

        self.ekf: ExtendedKalmanFilter = ExtendedKalmanFilter(dim_x=4, dim_z=1)
        self.ekf.x = np.array([[0.5, 0.0, 0.0, 0.5]]).T
        self.ekf.P = np.eye(4) * 100.0

        self.last_update_time: float = time.time()

        print(f"Added sensors {self.scanners}")

    def _update_matrices_for_dt(self, dt: float):
        """Dynamically update F and Q for the actual elapsed time dt."""

        self.ekf.F = np.array(
            [[1, dt, 0, 0], [0, 1, 0, 0], [0, 0, 1, dt], [0, 0, 0, 1]]
        )

        self.ekf.Q = Q_discrete_white_noise(dim=2, dt=dt, var=0.1, block_size=2)

    def _hx(self, x, active_positions):
        return np.array(
            [
                np.sqrt((x[0, 0] - s[0]) ** 2 + (x[2, 0] - s[1]) ** 2)
                for s in active_positions
            ]
        )

    def _HJacobian(self, x, active_positions):
        M = len(active_positions)
        H = np.zeros((M, 4))
        for i, s in enumerate(active_positions):
            dist: float = np.sqrt((x[0, 0] - s[0]) ** 2 + (x[2, 0] - s[1]) ** 2)
            dist = max(dist, 1e-6)

            H[i, 0] = (x[0, 0] - s[0]) / dist
            H[i, 2] = (x[2, 0] - s[1]) / dist
        return H

    def ingest_measurements(self, raw_readings: dict[str, list[float]]):
        now = time.time()
        dt = now - self.last_update_time
        if dt < 0.01:
            return

        dt = min(dt, 1.0)
        self.last_update_time = now

        self._update_matrices_for_dt(dt)
        self.ekf.predict()

        for scanner_id, values in raw_readings.items():
            if values and scanner_id in self.scanners:
                z_val = np.mean(values)
                var_val = self.base_variance / len(values)
                scanner_pos = [self.scanners[scanner_id]]

                self.ekf.update(
                    z=np.array([z_val]),
                    HJacobian=self._HJacobian,
                    Hx=self._hx,
                    R=np.array([[var_val]]),
                    args=(scanner_pos,),
                    hx_args=(scanner_pos,),
                )

    def get_state(self) -> EkfCorrection:
        """Returns the current estimated position and velocity."""
        return EkfCorrection(
            float(self.ekf.x[0, 0]),
            float(self.ekf.x[1, 0]),
            float(self.ekf.x[2, 0]),
            float(self.ekf.x[3, 0]),
        )

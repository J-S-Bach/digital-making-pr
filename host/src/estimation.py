import time
from typing import Any, NamedTuple

import numpy as np
from filterpy.common import Q_discrete_white_noise
from filterpy.kalman import ExtendedKalmanFilter
from numpy.typing import NDArray

from src.incoming_data_handler import TECHNOLOGY, EstimatedDistance


class Measurement(NamedTuple):
    technology: TECHNOLOGY
    estimated_distance: EstimatedDistance
    device_id: str


class LiveEKFTracker:
    def __init__(
        self,
        scanner_locations: dict[str, list[float]],
        base_noise_variance: float = 0.5,
    ):
        self.scanners: dict[str, NDArray[Any]] = {
            k: np.array(v) for k, v in scanner_locations.items()
        }
        self.base_variance: float = base_noise_variance

        self.ekf: ExtendedKalmanFilter = ExtendedKalmanFilter(dim_x=4, dim_z=1)
        self.ekf.x = np.array([[0.0, 0.0, 0.0, 0.0]]).T
        self.ekf.P = np.eye(4) * 100.0

        self.last_update_time: float = time.time()

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
        """
        Call this whenever new data arrives from your transport layer (Socket/MQTT/Serial).
        Format: {"scanner_A": [5.1, 5.0], "scanner_B": [10.2]}
        """
        now = time.time()
        dt = now - self.last_update_time

        if dt <= 0.0:
            dt = 0.001

        self.last_update_time = now

        self._update_matrices_for_dt(dt)

        self.ekf.predict()

        active_positions = []
        averaged_z = []
        scaled_variances = []

        for scanner_id, values in raw_readings.items():
            if values and scanner_id in self.scanners:
                N = len(values)
                active_positions.append(self.scanners[scanner_id])
                averaged_z.append(np.mean(values))
                scaled_variances.append(self.base_variance / N)

        if averaged_z:
            z = np.array(averaged_z)
            R = np.diag(scaled_variances)

            self.ekf.update(
                z=z,
                HJacobian=self._HJacobian,
                Hx=self._hx,
                R=R,
                args=(active_positions,),
                hx_args=(active_positions,),
            )

    def get_state(self) -> dict[str, float]:
        """Returns the current estimated position and velocity."""
        return {
            "x": float(self.ekf.x[0, 0]),
            "vx": float(self.ekf.x[1, 0]),
            "y": float(self.ekf.x[2, 0]),
            "vy": float(self.ekf.x[3, 0]),
        }

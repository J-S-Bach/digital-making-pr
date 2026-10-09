import time
from datetime import datetime
from typing import Any

import numpy as np
from filterpy.common import Q_discrete_white_noise
from filterpy.kalman import ExtendedKalmanFilter
from numpy.typing import NDArray
from scipy.linalg import block_diag

from src.estimations.ekf_layout import DevicePosition, EkfCorrection, EkfLayout


class EkfMultipleBadgeNonLinearWithoutInitialVelocity(EkfLayout):
    def __init__(
        self,
        scanner_locations: list[DevicePosition],
        base_noise_variance: float = 0.1,
    ):
        self.scanners: dict[str, NDArray[Any]] = {
            scanner_location.device_id: np.array(
                [scanner_location.position.x, scanner_location.position.y]
            )
            for scanner_location in scanner_locations
        }
        self.base_variance: float = base_noise_variance
        self.descriptor = "Multiple Badges Non Linear Without Initial Velocity"

        self.ekf: ExtendedKalmanFilter = ExtendedKalmanFilter(dim_x=4, dim_z=1)
        self.ekf.x = np.array([[0.0, 0.0, 0.0, 0.0]]).T
        self.ekf.P = np.eye(4) * 100.0

        self.last_update_time: float | None = None

        self.measurement_buffer: dict[str, list[float]] = {}

        print(f"Added sensors {self.scanners}")

    @staticmethod
    def _parse_timestamp(ts: datetime | float | None) -> float:
        """Converts datetime, float, or None to Unix timestamp in seconds."""
        if ts is None:
            return time.time()
        if isinstance(ts, datetime):
            return ts.timestamp()
        return float(ts)

    def _update_matrices_for_dt(self, dt: float):
        """Dynamically update F and Q for the actual elapsed time dt."""
        self.ekf.F = np.array(
            [[1, dt, 0, 0], [0, 1, 0, 0], [0, 0, 1, dt], [0, 0, 0, 1]]
        )

        q_1d = Q_discrete_white_noise(dim=2, dt=dt, var=0.01)
        self.ekf.Q = block_diag(q_1d, q_1d)

    def _hx(
        self, x: NDArray[Any], active_positions: list[NDArray[Any]]
    ) -> NDArray[Any]:
        """Calculates expected range for M active scanners. Returns shape (M, 1)."""
        ranges = [
            np.sqrt((x[0, 0] - s[0]) ** 2 + (x[2, 0] - s[1]) ** 2)
            for s in active_positions
        ]
        return np.array(ranges).reshape(-1, 1)

    def _HJacobian(
        self, x: NDArray[Any], active_positions: list[NDArray[Any]]
    ) -> NDArray[Any]:

        M = len(active_positions)
        H = np.zeros((M, 4))

        for i, s in enumerate(active_positions):
            dx = x[0, 0] - s[0]
            dy = x[2, 0] - s[1]
            dist = np.sqrt(dx**2 + dy**2)

            if dist < 0.2:
                H[i, 0] = dx / 0.2
                H[i, 2] = dy / 0.2
            else:
                H[i, 0] = dx / dist
                H[i, 2] = dy / dist

        return H

    def add_measurement(
        self,
        scanner_id: str,
        distance: float,
        timestamp: datetime | float | None = None,
    ):
        """Collects incoming measurements into a buffer over time."""
        if scanner_id not in self.scanners or distance <= 0.05:
            return

        if scanner_id not in self.measurement_buffer:
            self.measurement_buffer[scanner_id] = []

        self.measurement_buffer[scanner_id].append(distance)

    def process_buffered_batch(self, timestamp: datetime | float | None = None):
        """Flushes the buffer and performs a single batched EKF update step."""
        if not self.measurement_buffer:
            return

        now = self._parse_timestamp(timestamp)

        if self.last_update_time is None:
            dt = 0.05
        else:
            dt = now - self.last_update_time

        dt = max(dt, 0.001)
        dt = min(dt, 1.0)
        self.last_update_time = now

        self._update_matrices_for_dt(dt)
        self.ekf.predict()

        z_list = []
        active_positions = []
        r_variances = []

        # Process aggregated measurements from each scanner in the buffer
        for scanner_id, distances in self.measurement_buffer.items():
            if not distances:
                continue

            avg_dist = float(np.mean(distances))
            z_list.append(avg_dist)
            active_positions.append(self.scanners[scanner_id])

            # Distance-dependent variance scaling
            d2_var = self.base_variance * (avg_dist**2)
            var = max(0.1, d2_var / len(distances))
            r_variances.append(var)

        # Clear buffer immediately after pulling data
        self.measurement_buffer.clear()

        if not z_list:
            return

        # Build batched matrices
        Z = np.array(z_list).reshape(-1, 1)
        R = np.diag(r_variances)

        # Dynamically set measurement dimension dim_z and update
        self.ekf.dim_z = len(z_list)
        self.ekf.update(
            z=Z,
            HJacobian=self._HJacobian,
            Hx=self._hx,
            R=R,
            args=(active_positions,),
            hx_args=(active_positions,),
        )

        self._apply_state_bounds()

    def _apply_state_bounds(self):
        """Clamps state variables to physical room boundaries and velocity caps."""
        self.ekf.x[1, 0] = np.clip(self.ekf.x[1, 0], -3.0, 3.0)  # max vx (m/s)
        self.ekf.x[3, 0] = np.clip(self.ekf.x[3, 0], -3.0, 3.0)  # max vy (m/s)

    def get_state(self, timestamp: datetime | float | None = None) -> EkfCorrection:
        """Flushes buffered measurements and returns current estimated position and velocity."""
        self.process_buffered_batch(timestamp=timestamp)
        return EkfCorrection(
            float(self.ekf.x[0, 0]),
            float(self.ekf.x[1, 0]),
            float(self.ekf.x[2, 0]),
            float(self.ekf.x[3, 0]),
        )

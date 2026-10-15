import time
from datetime import datetime
from typing import Any

import numpy as np
from filterpy.common import Q_discrete_white_noise
from filterpy.kalman import ExtendedKalmanFilter
from numpy.typing import NDArray
from scipy.linalg import block_diag

from src.estimations.ekf_layout import DevicePosition, EkfCorrection, EkfLayout


class EkfEnforceRegularUpdates(EkfLayout):
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

        self.ekf: ExtendedKalmanFilter = ExtendedKalmanFilter(dim_x=4, dim_z=1)
        self.ekf.x = np.array([[0.5, 0.0, 0.5, 0.0]]).T
        self.ekf.P = np.eye(4) * 100.0

        self.last_update_time: float | None = None
        self.measurement_buffer: dict[str, list[float]] = {}

    @property
    def descriptor(self) -> str:
        return "EnforcedRegularUpdates"

    @staticmethod
    def _parse_timestamp(ts: datetime | float | None) -> float:
        """Converts datetime, float, or None to Unix timestamp in seconds."""
        if ts is None:
            return time.time()
        if isinstance(ts, datetime):
            return ts.timestamp()
        return float(ts)

    def _update_matrices_for_dt(self, dt: float) -> None:
        self.ekf.F = np.array(
            [
                [1.0, dt, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, dt],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )

        q_var = 0.01 / dt if dt > 0 else 0.01

        q_1d = Q_discrete_white_noise(dim=2, dt=dt, var=q_var)
        self.ekf.Q = block_diag(q_1d, q_1d)

    @staticmethod
    def _hx_single(x: NDArray[Any], scanner_pos: NDArray[Any]) -> NDArray[Any]:
        dx = x[0, 0] - scanner_pos[0]
        dy = x[2, 0] - scanner_pos[1]
        return np.array([[np.sqrt(dx**2 + dy**2)]])

    @staticmethod
    def _HJacobian_single(x: NDArray[Any], scanner_pos: NDArray[Any]) -> NDArray[Any]:
        dx = x[0, 0] - scanner_pos[0]
        dy = x[2, 0] - scanner_pos[1]
        dist = max(np.sqrt(dx**2 + dy**2), 1e-4)
        return np.array([[dx / dist, 0.0, dy / dist, 0.0]])

    def add_measurement(
        self,
        scanner_id: str,
        distance: float,
        timestamp: datetime | float | None = None,
    ) -> None:
        if scanner_id not in self.scanners or distance <= 0.05:
            return

        if scanner_id not in self.measurement_buffer:
            self.measurement_buffer[scanner_id] = []

        self.measurement_buffer[scanner_id].append(distance)

    def process_buffered_batch(self, timestamp: datetime | float | None = None) -> None:
        now = self._parse_timestamp(timestamp)

        if self.last_update_time is None:
            dt = 0.05
        else:
            dt = now - self.last_update_time

        if dt <= 0:
            dt = 0.001

        self.last_update_time = now

        self._update_matrices_for_dt(dt)
        self.ekf.predict()

        if self.measurement_buffer:
            for scanner_id, distances in list(self.measurement_buffer.items()):
                if not distances:
                    continue

                scanner_pos = self.scanners[scanner_id]
                dist_meas = float(np.median(distances))
                num_samples = len(distances)

                r_var = max(0.05, (self.base_variance * (dist_meas**2)) / num_samples)

                hx_pred = self._hx_single(self.ekf.x, scanner_pos)[0, 0]
                residual = dist_meas - hx_pred

                H = self._HJacobian_single(self.ekf.x, scanner_pos)
                S = float((H @ self.ekf.P @ H.T)[0, 0] + r_var)

                if (residual**2) > 16.0 * S:
                    r_var *= 10.0

                self.ekf.update(
                    z=np.array([[dist_meas]]),
                    HJacobian=self._HJacobian_single,
                    Hx=self._hx_single,
                    R=np.array([[r_var]]),
                    args=(scanner_pos,),
                    hx_args=(scanner_pos,),
                )

            self.measurement_buffer.clear()

        self._apply_velocity_caps()

    def _apply_velocity_caps(self) -> None:
        max_speed = 3.0
        self.ekf.x[1, 0] = np.clip(self.ekf.x[1, 0], -max_speed, max_speed)
        self.ekf.x[3, 0] = np.clip(self.ekf.x[3, 0], -max_speed, max_speed)

    def get_state(self, timestamp: datetime | float | None = None) -> EkfCorrection:
        self.process_buffered_batch(timestamp=timestamp)
        return EkfCorrection(
            x=float(self.ekf.x[0, 0]),
            vx=float(self.ekf.x[1, 0]),
            y=float(self.ekf.x[2, 0]),
            vy=float(self.ekf.x[3, 0]),
        )

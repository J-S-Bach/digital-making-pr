import time
from typing import Any, NamedTuple, Self, override

import numpy as np
from filterpy.common import Q_discrete_white_noise
from filterpy.kalman import ExtendedKalmanFilter
from numpy.typing import NDArray
from scipy.linalg import block_diag

from src.estimations.ekf_layout import DevicePosition, EkfCorrection, EkfLayout


class EkfSingleBadgeNonLinear(EkfLayout):
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
        self.ekf.F = np.array(
            [[1, dt, 0, 0], [0, 1, 0, 0], [0, 0, 1, dt], [0, 0, 0, 1]]
        )

        q_1d = Q_discrete_white_noise(dim=2, dt=dt, var=0.1)
        self.ekf.Q = block_diag(q_1d, q_1d)

    def _hx(self, x: NDArray[Any], scanner_pos: NDArray[Any]) -> NDArray[Any]:

        dist = np.sqrt(
            (x[0, 0] - scanner_pos[0]) ** 2 + (x[2, 0] - scanner_pos[1]) ** 2
        )
        return np.array([[dist]])

    def _HJacobian(self, x: NDArray[Any], scanner_pos: NDArray[Any]) -> NDArray[Any]:
        """Calculates 1x4 Jacobian matrix."""
        H = np.zeros((1, 4))
        dist: float = np.sqrt(
            (x[0, 0] - scanner_pos[0]) ** 2 + (x[2, 0] - scanner_pos[1]) ** 2
        )
        dist = max(dist, 1e-6)

        H[0, 0] = (x[0, 0] - scanner_pos[0]) / dist
        H[0, 2] = (x[2, 0] - scanner_pos[1]) / dist
        return H

    @override
    def add_measurement(self, scanner_id: str, distance: float):
        """Process readings"""
        if scanner_id not in self.scanners or distance <= 0.05:
            return

        now = time.time()
        dt = now - self.last_update_time

        # Predict state forward if sufficient time has elapsed
        if dt >= 0.01:
            dt = min(dt, 1.0)
            self.last_update_time = now
            self._update_matrices_for_dt(dt)
            self.ekf.predict()

        scanner_pos = self.scanners[scanner_id]

        # Scaled variance R based on distance (Fixes Flaw #4)
        variance_value = max(0.1, self.base_variance * (distance**2))
        R = np.array([[variance_value]])

        # Execute single scalar update (Fixes Flaw #1 and #2)
        self.ekf.update(
            z=np.array([[distance]]),
            HJacobian=self._HJacobian,
            Hx=self._hx,
            R=R,
            args=(scanner_pos,),
            hx_args=(scanner_pos,),
        )

        # Enforce boundary constraints (Optional state bounds guard)
        self._apply_state_bounds()

    def _apply_state_bounds(self):
        """Clamps state variables to physical room boundaries and velocity caps."""
        # Optional: Adjust bounds to match your environment dimensions
        self.ekf.x[1, 0] = np.clip(self.ekf.x[1, 0], -3.0, 3.0)  # max vx (m/s)
        self.ekf.x[3, 0] = np.clip(self.ekf.x[3, 0], -3.0, 3.0)  # max vy (m/s)

    def get_state(self) -> EkfCorrection:
        """Returns the current estimated position and velocity."""
        return EkfCorrection(
            float(self.ekf.x[0, 0]),
            float(self.ekf.x[1, 0]),
            float(self.ekf.x[2, 0]),
            float(self.ekf.x[3, 0]),
        )

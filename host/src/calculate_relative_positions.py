from dataclasses import dataclass
from functools import reduce
from typing import NamedTuple

import numpy as np
from numpy.typing import NDArray

from src.discover_clients import DeviceData
from src.estimations.ekf_layout import DevicePosition, Position
from src.technology_handler import NodeCalibrationData


@dataclass
class NodeStats:
    target_device: DeviceData
    mean_m: float
    variance: float
    inverse_variance: float
    weight: float


class Measurement(NamedTuple):
    mean: float
    inv_var: float
    entry: NodeStats


@dataclass
class DeviceNodeStats:
    scanning_device: DeviceData
    data: list[NodeStats]


class FusedVarianceData(NamedTuple):
    fused_distance_m: float
    total_nodes: int
    data_entries: list[DeviceNodeStats]


# This is called N-Node Inverse-Variance Weighting. Include and explain this in report. Basically, the more variance the measurement has, the less it gets used for the average. easy peasy. https://en.wikipedia.org/wiki/Inverse-variance_weighting


# AI Generated (Gemini)
def classical_mds(dist_matrix: np.ndarray, dims: int = 2) -> NDArray[np.float64]:
    """Computes N-dimensional coordinates from a distance matrix."""
    n = dist_matrix.shape[0]
    # 1. Centering matrix H = I - (1/n)*1
    H = np.eye(n) - np.ones((n, n)) / n
    # 2. Double-center the squared distance matrix
    B = -0.5 * H @ (dist_matrix**2) @ H
    # 3. Eigen-decomposition
    evals, evecs = np.linalg.eigh(B)
    # 4. Sort descending and take top components
    idx = np.argsort(evals)[::-1]
    evals, evecs = evals[idx], evecs[:, idx]

    return evecs[:, :dims] * np.sqrt(np.maximum(evals[:dims], 0))


def filter_iqr(data: np.ndarray) -> np.ndarray:
    """Removes transient distance spikes using Interquartile Range."""
    q25, q75 = map(float, np.percentile(data, [25, 75]))
    iqr = q75 - q25
    filtered = data[(data >= q25 - 1.5 * iqr) & (data <= q75 + 1.5 * iqr)]
    return filtered if len(filtered) > 0 else data


def fuse_n_nodes_inverse_variance(
    node_data: list[NodeCalibrationData],
) -> FusedVarianceData:
    """Fuses pre-calculated distance arrays from N static ESP32 nodes."""
    stats: list[DeviceNodeStats] = []

    # 1. Prepare node data with node distances.
    for node in node_data:
        device_node_stats = DeviceNodeStats(data=[], scanning_device=node.source_device)

        for target in node.peer_measurements:
            arr = filter_iqr(np.array(target.distances, dtype=float))
            mean = float(np.mean(arr))
            var = max(float(np.var(arr, ddof=1)), 1e-4)
            inv_var = 1.0 / var

            entry: NodeStats = NodeStats(
                target_device=target.target_device,
                mean_m=round(mean, 3),
                variance=round(var, 4),
                inverse_variance=round(inv_var, 4),
                weight=0.0,
            )

            device_node_stats.data.append(entry)

        stats.append(device_node_stats)
    if not node_data:
        return FusedVarianceData(fused_distance_m=0, data_entries=[], total_nodes=0)

    # 2. Compute weights and overall fused distance (just in case its needed)
    flat_stats = reduce(list.__add__, [stat.data for stat in stats])
    all_inv_vars = [flat_stat.inverse_variance for flat_stat in flat_stats]
    total_inv_var = sum(all_inv_vars)

    fused_distance = 0.0

    for stat in flat_stats:
        weight = stat.inverse_variance / total_inv_var
        stat.weight = round(weight, 3)
        fused_distance += stat.mean_m * weight

    # Yeah return that math!
    return FusedVarianceData(
        fused_distance_m=round(fused_distance, 3),
        total_nodes=len(node_data),
        data_entries=stats,
    )


def generate_device_positions(
    fused_data: FusedVarianceData,
    primary_id: str | None = None,
    secondary_id: str | None = None,
    ref_positive_y_id: str | None = None,
) -> list[DevicePosition]:
    """Creates a list of device positions based on estimations, with optional anchor
    alignment and reflection correction.
    """

    # Extract unique devices
    devices = list(
        {
            e.scanning_device.device_id: e.scanning_device
            for e in fused_data.data_entries
        }.values()
    )
    if not devices:
        return []

    idx = {dev.device_id: i for i, dev in enumerate(devices)}
    dist = np.zeros((len(devices), len(devices)))

    # Populate distance matrix
    for entry in fused_data.data_entries:
        i = idx[entry.scanning_device.device_id]
        for node in entry.data:
            if node.target_device.device_id in idx:
                j = idx[node.target_device.device_id]
                dist[i, j] = dist[j, i] = node.mean_m

    coords = classical_mds(dist, dims=2)
    pos_map = {dev.device_id: coords[i] for i, dev in enumerate(devices)}

    if primary_id and secondary_id:
        if primary_id in pos_map and secondary_id in pos_map:
            origin = pos_map[primary_id]
            pos_map = {dev_id: c - origin for dev_id, c in pos_map.items()}

            sec_vec = pos_map[secondary_id]
            angle = -np.arctan2(sec_vec[1], sec_vec[0])

            rot_matrix = np.array(
                [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
            )

            pos_map = {dev_id: rot_matrix @ c for dev_id, c in pos_map.items()}

    if (
        ref_positive_y_id
        and ref_positive_y_id in pos_map
        and pos_map[ref_positive_y_id][1] < 0
    ):
        pos_map = {dev_id: np.array([c[0], -c[1]]) for dev_id, c in pos_map.items()}

    return [
        DevicePosition.from_DeviceData(
            device_data=dev,
            position=Position(
                round(float(pos_map[dev.device_id][0]), 3),
                round(float(pos_map[dev.device_id][1]), 3),
            ),
        )
        for dev in devices
    ]

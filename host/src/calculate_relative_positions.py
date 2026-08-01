from dataclasses import dataclass
from typing import NamedTuple, TypedDict

import numpy as np

from src.technology_handler import NodeCalibrationData


@dataclass
class NodeStats:
    mean_m: float
    variance: float
    weight: float


class Measurement(NamedTuple):
    mean: float
    inv_var: float
    entry: NodeStats


# This is called N-Node Inverse-Variance Weighting. Include and explain this in report. Basically, the more variance the measurement has, the less it gets used for the average. easy peasy. https://en.wikipedia.org/wiki/Inverse-variance_weighting


def filter_iqr(data: np.ndarray) -> np.ndarray:
    """Removes transient distance spikes using Interquartile Range."""
    q25, q75 = map(float, np.percentile(data, [25, 75]))
    iqr = q75 - q25
    filtered = data[(data >= q25 - 1.5 * iqr) & (data <= q75 + 1.5 * iqr)]
    return filtered if len(filtered) > 0 else data


def fuse_n_nodes_inverse_variance(node_data: list[NodeCalibrationData]):
    """Fuses pre-calculated distance arrays from N static ESP32 nodes."""
    stats: dict[str, dict[str, NodeStats]] = {}
    measurements: list[Measurement] = []

    for node in node_data:
        source_device_id = node.source_device["device_id"]
        stats[source_device_id] = {}

        for target in node.peer_measurements:
            tgt_mac = target.target_device["bluetooth_mac"]

            arr = filter_iqr(np.array(target.distances, dtype=float))
            mean = float(np.mean(arr))
            var = max(float(np.var(arr, ddof=1)), 1e-4)
            inv_var = 1.0 / var

            entry: NodeStats = NodeStats(
                mean_m=round(mean, 3),
                variance=round(var, 4),
                weight=0.0,
            )

            stats[source_device_id][tgt_mac] = entry

            measurements.append(Measurement(entry=entry, inv_var=inv_var, mean=mean))

    if not measurements:
        return {"fused_distance_m": 0.0, "total_nodes": 0, "node_stats": {}}

    # 2. Compute weights and final fused distance
    total_inv_var = sum(m.inv_var for m in measurements)
    fused_distance = 0.0

    for m in measurements:
        weight = m.inv_var / total_inv_var
        m.entry.weight = round(weight, 3)
        fused_distance += m.mean * weight

    return {
        "fused_distance_m": round(fused_distance, 3),
        "total_nodes": len(node_data),
        "node_stats": stats,
    }

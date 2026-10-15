import csv
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

from dateutil import parser

from src.estimations.ekf_layout import DevicePosition, EkfLayout, Position


class TestCase(NamedTuple):
    ekf: EkfLayout
    name: str
    data: list[tuple[str, float, datetime, float, float]]


class TestSet(NamedTuple):
    """
    Contains everything that we need from one file that we are testing.
    """

    name: str
    data_points: list[tuple[str, float, datetime, float, float]]
    scanner_locations: list[DevicePosition]


def load_test_sets() -> list[TestSet]:
    """
    Loads data from testing/test_data folder.
    Takes all files that are placed there and expects files to be formatted as defined in src/main.py, even though it will ignore the calculated test data, and instead only pulls device id, measured distance, and position of trackers.
    """
    folder = Path("testing/test_data")
    test_sets = []

    if not folder.exists():
        return []

    for file_path in folder.glob("*"):
        if not file_path.is_file():
            continue

        data_points: list[tuple[str, float, datetime, float, float]] = []
        unique_scanners = {}

        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                device_id = str(row["device_id"])
                distance = float(row["tracked_device_raw_distance_data"])
                timestamp = parser.parse(row["timestamp"])
                data_points.append(
                    (
                        device_id,
                        distance,
                        timestamp,
                        float(row["tracking_device_position_x"]),
                        float(row["tracking_device_position_y"]),
                    )
                )

                if device_id not in unique_scanners:
                    unique_scanners[device_id] = DevicePosition(
                        device_id=device_id,
                        position=Position(
                            x=float(row["tracking_device_position_x"]),
                            y=float(row["tracking_device_position_y"]),
                        ),
                        # TODO: Place matching properties in csv, even if unused here. Logging but unused > no logging but needed
                        bluetooth_mac="",
                        hostname="",
                        ip_address="",
                    )

        test_sets.append(
            TestSet(
                name=file_path.stem,
                data_points=data_points,
                scanner_locations=list(unique_scanners.values()),
            )
        )

    return test_sets

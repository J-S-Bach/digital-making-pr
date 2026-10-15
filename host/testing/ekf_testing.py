import math
from datetime import datetime, timedelta
from time import time
from typing import NamedTuple

from src.data_logger import DataLogger
from src.estimations.ekf_enforced_regular_intervalls import (
    EkfEnforceRegularUpdates,
)
from src.estimations.ekf_layout import EkfCorrection, EkfLayout, Position
from src.estimations.ekf_multiple_badge_non_linear_initial_velocity_05 import (
    EkfMultipleBadgeNonLinearWithVelocity,
)
from src.estimations.ekf_multiple_badge_non_linear_no_initial_velocity import (
    EkfMultipleBadgeNonLinearWithoutInitialVelocity,
)
from src.estimations.ekf_multiple_badges_sequential_gated_dropping_initial_velocity_05 import (
    EkfMultipleBadgesSequentialGatedWithInitialVelocity,
)
from src.estimations.ekf_multiple_badges_sequential_gated_dropping_no_initial_velocity import (
    EkfMultipleBadgesSequentialGatedNoVelocity,
)
from src.estimations.ekf_single_badge_non_linear_initial_velocity_05 import (
    EkfSingleBadgeNonLinearWithInitialVelocity,
)
from src.estimations.ekf_single_badge_non_linear_no_initial_velocit import (
    EkfSingleBadgeNonLinearNoVelocity,
)
from testing.load_test_sets import TestCase, TestSet, load_test_sets

POSSIBLE_FILTERS: list[type[EkfLayout]] = [
    EkfMultipleBadgeNonLinearWithVelocity,
    EkfMultipleBadgeNonLinearWithoutInitialVelocity,
    EkfSingleBadgeNonLinearNoVelocity,
    EkfSingleBadgeNonLinearWithInitialVelocity,
    EkfMultipleBadgesSequentialGatedNoVelocity,
    EkfMultipleBadgesSequentialGatedWithInitialVelocity,
    EkfEnforceRegularUpdates,
]

POSSIBLE_NOISE_VARIANCES: list[float] = [0.1, 0.5, 1, 2, 3, 5, 10, 20, 35, 50, 100]


class EkfAndRealDataPoint(NamedTuple):
    ekf: EkfCorrection
    actual: Position
    timestamp: datetime
    anchor: Position
    tracking_device_id: str


class TestResult(NamedTuple):
    results: list[EkfAndRealDataPoint]
    rmse: float
    mae: float
    max_error: float


speed_meters_per_second = 0.0725
angle_degrees = 30
# Angle in radians expected by python.
angle_radians = math.radians(angle_degrees)
distance_from_0_point = 2.5


def get_actual_position(timedelta: timedelta) -> Position:
    """
    Takes current time and (or step index?) and returns the position that should actually be returned.
    Change this depending on test.
    """

    passed_distance_meters = (
        timedelta.seconds + timedelta.microseconds / 1000000
    ) * speed_meters_per_second

    leftover_distance = distance_from_0_point - passed_distance_meters

    # X Formula: x = distance * cos(angle)
    real_x_coordinate = leftover_distance * math.cos(angle_radians)

    # Y Formula: y = distance * sin(angle)
    real_y_coordinate = leftover_distance * math.sin(angle_radians)

    # print(f"Calculated {real_x_coordinate}/{real_y_coordinate}")

    return Position(x=real_x_coordinate, y=real_y_coordinate)


def calculate_results(
    ekf_and_real_comparison: list[EkfAndRealDataPoint],
) -> TestResult:
    """
    Calculating the
        - Root Square Mean Error (rmse), which penalizes large errors more heavily.
        - Max Error: The maximum error happening.
        - Mean absolute Error (mae). The error quote without penalizing errors differently.
    """
    if not ekf_and_real_comparison:
        return TestResult(results=[], rmse=0.0, mae=0.0, max_error=0.0)

    errors = [
        math.hypot(entry.ekf.x - entry.actual.x, entry.ekf.y - entry.actual.y)
        for entry in ekf_and_real_comparison
    ]

    rmse = math.sqrt(sum(e**2 for e in errors) / len(errors))
    mae = sum(errors) / len(errors)
    max_error = max(errors)

    return TestResult(ekf_and_real_comparison, rmse, mae, max_error)


def performance_testing():
    test_cases: list[TestCase] = []
    test_sets: list[TestSet] = load_test_sets()

    for kalman_filter in POSSIBLE_FILTERS:
        for noise_variance in POSSIBLE_NOISE_VARIANCES:
            for test_set in test_sets:
                test_cases.append(
                    TestCase(
                        data=test_set.data_points,
                        name=f"{test_set.name}_{noise_variance}_{kalman_filter}",
                        ekf=kalman_filter(
                            base_noise_variance=noise_variance,
                            scanner_locations=test_set.scanner_locations,
                        ),
                    )
                )

    test_case_logger = DataLogger(
        [
            "actual_x",
            "actual_y",
            "ekf_x",
            "ekf_y",
            "tracking_device_position_x",
            "tracking_device_position_y",
            "tracking_device_id",
            "overall_rmse",
            "overall_max_error",
            "overall_mae",
            "noise_variance",
            "algorithm_name",
            "timestamp",
        ],
        f"test_results_{time()}",
    )

    for test_case in test_cases:
        raw_test_case_results: list[EkfAndRealDataPoint] = []
        first_datetime = None

        for test_set_data_point in test_case.data:
            (scanner_id, distance, timestamp, anchor_x, anchor_y) = test_set_data_point

            if first_datetime is None:
                first_datetime = timestamp

            passed_time = timestamp - first_datetime

            actual_position = get_actual_position(passed_time)

            test_case.ekf.add_measurement(scanner_id, distance, timestamp=timestamp)
            ekf_correction = test_case.ekf.get_state(timestamp=timestamp)

            raw_test_case_results.append(
                EkfAndRealDataPoint(
                    ekf=ekf_correction,
                    actual=actual_position,
                    timestamp=timestamp,
                    anchor=Position(anchor_x, anchor_y),
                    tracking_device_id=scanner_id,
                )
            )

        calculated_test_set = calculate_results(raw_test_case_results)

        for result in calculated_test_set.results:
            test_case_logger.write_data_point(
                [
                    result.actual.x,
                    result.actual.y,
                    result.ekf.x,
                    result.ekf.y,
                    result.anchor.x,
                    result.anchor.y,
                    result.tracking_device_id,
                    calculated_test_set.rmse,
                    calculated_test_set.max_error,
                    calculated_test_set.mae,
                    test_case.ekf.base_variance,
                    test_case.ekf.descriptor,
                    str(result.timestamp),
                ]
            )

        # print(
        #     f"Got test set results for test case {test_case.name}: RMSE of {calculated_test_set.rmse}"
        # )


if __name__ == "__main__":
    performance_testing()

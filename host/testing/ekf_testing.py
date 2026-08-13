import math
from datetime import datetime
from typing import NamedTuple

from src.data_logger import DataLogger
from src.estimations.ekf_layout import EkfCorrection, EkfLayout, Position
from src.estimations.ekf_multiple_badge_non_linear import EkfMultipleBadgeNonLinear
from src.estimations.ekf_single_badge_non_linear import EkfSingleBadgeNonLinear
from testing.load_test_sets import TestCase, TestSet, load_test_sets

POSSIBLE_FILTERS: list[type[EkfLayout]] = [
    EkfMultipleBadgeNonLinear,
    EkfSingleBadgeNonLinear,
]

POSSIBLE_NOISE_VARIANCES: list[float] = [0.1, 0.5, 1]


class TestResultEntry(NamedTuple):
    actual: Position
    ekf: Position


class TestResult(NamedTuple):
    results: list[TestResultEntry]
    rmse: float
    mae: float
    max_error: float


class EkfAndRealDataPoint(NamedTuple):
    ekf: EkfCorrection
    actual: Position


def save_test_result() -> None:
    """
    This makes sure to actually be able to see and maybe visualize the results.
    """
    pass


# Do we also need a start point?
def get_actual_position(timestamp: datetime) -> Position:
    """
    Takes current time and (or step index?) and returns the position that should actually be returned.
    Change this depending on test.
    """
    return Position(x=0.5, y=0.5)


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

    results = [
        TestResultEntry(actual=item.actual, ekf=Position(x=item.ekf.x, y=item.ekf.y))
        for item in ekf_and_real_comparison
    ]

    errors = [
        math.hypot(entry.ekf.x - entry.actual.x, entry.ekf.y - entry.actual.y)
        for entry in results
    ]

    rmse = math.sqrt(sum(e**2 for e in errors) / len(errors))
    mae = sum(errors) / len(errors)
    max_error = max(errors)

    return TestResult(results, rmse, mae, max_error)


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

    for test_case in test_cases:
        raw_test_case_results: list[EkfAndRealDataPoint] = []
        test_case_logger = DataLogger(
            [
                "actual_x",
                "actual_y",
                "ekf_x",
                "ekf_y",
                "overall_rmse",
                "overall_max_error",
                "overall_mae",
            ],
            f"test_results_{test_case.name}",
        )

        for test_set_data_point in test_case.data:
            (scanner_id, distance, timestamp) = test_set_data_point
            actual_position = get_actual_position(timestamp)

            test_case.ekf.add_measurement(scanner_id, distance)
            ekf_correction = test_case.ekf.get_state()

            raw_test_case_results.append(
                EkfAndRealDataPoint(ekf=ekf_correction, actual=actual_position)
            )

        calculated_test_set = calculate_results(raw_test_case_results)

        for result in calculated_test_set.results:
            test_case_logger.write_data_point(
                [
                    result.actual.x,
                    result.actual.y,
                    result.ekf.x,
                    result.ekf.y,
                    calculated_test_set.rmse,
                    calculated_test_set.max_error,
                    calculated_test_set.mae,
                ]
            )

        print(
            f"Got test set results for test case {test_case.name}: RMSE of {calculated_test_set.rmse}"
        )


if __name__ == "__main__":
    performance_testing()

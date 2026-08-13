

from datetime import datetime
import math
from typing import NamedTuple


from src.estimations.ekf_layout import   EkfCorrection, EkfLayout, Position
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
    if not ekf_and_real_comparison:
        return TestResult(results=[], rmse=0.0)

    results = [
        TestResultEntry(
            actual=item.actual, ekf=Position(x=item.ekf.x, y=item.ekf.y)
        )
        for item in ekf_and_real_comparison
    ]

    total_squared_error = sum(
        (entry.ekf.x - entry.actual.x) ** 2
        + (entry.ekf.y - entry.actual.y) ** 2
        for entry in results
    )

    rmse = math.sqrt(total_squared_error / len(results))

    return TestResult(results=results, rmse=rmse)

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
                        ekf=kalman_filter(base_noise_variance=noise_variance, scanner_locations=test_set.scanner_locations)
                ))


    for test_case in test_cases:
        raw_test_case_results: list[EkfAndRealDataPoint] = []

        for test_set_data_point in test_case.data:

            (scanner_id, distance, timestamp) = test_set_data_point
            actual_position = get_actual_position(timestamp)

            test_case.ekf.add_measurement(scanner_id, distance)
            ekf_correction = test_case.ekf.get_state()

            raw_test_case_results.append(EkfAndRealDataPoint(ekf=ekf_correction, actual=actual_position))

        test_set_result = calculate_results(raw_test_case_results)


        print(f"Got test set results for test case {test_case.name}: RMSE of {test_set_result.rmse}")


if __name__ == "__main__":
    performance_testing()

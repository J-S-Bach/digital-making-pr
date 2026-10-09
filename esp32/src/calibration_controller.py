import math

# Log distance formula: relative to log_10(distance)
#
# Therefore, simple place: y = a+b*x
#
# y is RSSI
# P_0 is a (to solve!)
# N = -(b/10) => b = -10*N (also to solve!)

class MeasuredDataPoint:
    def __init__(self, distance: float, measurements: list[float]) -> None:
        self.real_distance: float = distance
        self.rssi_measurements: list[float] = measurements

class CalibrationController():
    def __init__(self):
        self.measured_data_points: list[MeasuredDataPoint] = []

    def get_results(self):
        return self._calculate_p0_and_n()

    def add_measurement(self, distance: float, measurements: list[float]):
        print(f"added measurement ({",".join(str(measurements))})")
        self.measured_data_points.append(MeasuredDataPoint(distance, measurements))


    def _calculate_p0_and_n(
        self,
    ) -> tuple[float, float]:
        x_data = []
        y_data = []

        measured_data = self.measured_data_points

        # Extract and log-transform distances
        for entry in measured_data:
            log_d = math.log10(entry.real_distance)
            print(entry.rssi_measurements)
            for rssi in entry.rssi_measurements:
                x_data.append(log_d)
                y_data.append(float(rssi))

        print(self.measured_data_points)
        print(x_data)

        n_samples = len(x_data)
        print(n_samples)
        mean_x = sum(x_data) / n_samples
        mean_y = sum(y_data) / n_samples

        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_data, y_data))
        denominator = sum((x - mean_x) ** 2 for x in x_data)

        slope = numerator / denominator
        intercept = mean_y - slope * mean_x

        # Map linear components to physical parameters
        optimal_P0 = intercept
        optimal_N = -slope / 10.0

        # Clamp parameters to physical bounds: P0 [-80, -30], N [1.0, 6.0]
        optimal_P0 = max(-80.0, min(-30.0, optimal_P0))
        optimal_N = max(1.0, min(6.0, optimal_N))

        print(f"Calibrated P0 (1m RSSI): {optimal_P0:.2f} dBm")
        print(f"Calibrated N (Path-loss exponent): {optimal_N:.2f}")

        return round(optimal_P0, 2), round(optimal_N, 2)

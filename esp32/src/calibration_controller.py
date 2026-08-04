import math

# Log distance formula: relative to log_10(distance)
#
# Therefore, simple place: y = a+b*x
#
# y is RSSI
# P_0 is a (to solve!)
# N = -(b/10) => b = -10*N (also to solve!)


def calibrate_p0_and_n(
    measured_data: list[dict[str, float | list[int]]],
) -> tuple[float, float]:
    x_data = []
    y_data = []

    # Extract and log-transform distances
    for entry in measured_data:
        log_d = math.log10(entry["actual_distance_m"])
        for rssi in entry["rssi_samples"]:
            x_data.append(log_d)
            y_data.append(float(rssi))

    n_samples = len(x_data)
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

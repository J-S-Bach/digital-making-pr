import asyncio
import sys
from asyncio import sleep
from datetime import UTC, datetime
from typing import Callable

from rich.prompt import Prompt

from src.calculate_relative_positions import (
    DeviceNodeStats,
    FusedVarianceData,
    NodeStats,
    fuse_n_nodes_inverse_variance,
    generate_device_positions,
)
from src.data_logger import DataLogger
from src.estimations.ekf_layout import DevicePosition, Position
from src.estimations.ekf_multiple_badges_sequential_gated_dropping_initial_velocity_05 import (
    EkfMultipleBadgesSequentialGatedWithInitialVelocity,
)
from src.host_on_website import GraphCoordinate, host_on_website
from src.incoming_data_handler import (
    TECHNOLOGY,
    DeviceId,
    EstimatedDistance,
    UDPCatcher,
)
from src.self_identification import get_own_ip
from src.technology_handler import TechnologyHandler

from .discover_clients import discover_clients

devices = discover_clients()

UDP_PORT = 6969
own_ip = get_own_ip()
target_udp_address = f"http://{own_ip}:{UDP_PORT}"


async def main():
    if len(devices) == 0:
        print("No Device Could be found...")
        return

    update_website: Callable[[GraphCoordinate], None] | None = None

    if "--gui" in sys.argv or "-g" in sys.argv:
        update_website = await host_on_website()

    data_handler = UDPCatcher(UDP_PORT)

    technology_handler = TechnologyHandler(devices, target_udp_address)

    position_estimations = technology_handler.scan_device_positions()

    technology_handler.activate_bluetooth()

    device_positions: list[DevicePosition] = []

    if position_estimations is not None:
        # fused_nodes = fuse_n_nodes_inverse_variance(position_estimations)
        # Anchor MDS positions
        select_device_string = [
            f"-  {device.hostname} [{index + 1}]\n"
            for index, device in enumerate(devices)
        ]

        zero_value: str = Prompt.ask(
            f"Select a device to be the zero point:\n{''.join(select_device_string)}",
            choices=[str(index + 1) for index, _ in enumerate(devices)],
            default="auto",
        )

        x_axis_device: str = Prompt.ask(
            f"Select the that is in the positive x value space:\n{''.join(select_device_string)}",
            choices=[str(index + 1) for index, _ in enumerate(devices)],
            default="auto",
        )

        y_axis_device: str = Prompt.ask(
            f"Select the that is in the positive y value space:\n{''.join(select_device_string)}",
            choices=[str(index + 1) for index, _ in enumerate(devices)],
            default="auto",
        )
        dev_A = devices[int(zero_value) - 1]
        dev_B = devices[int(x_axis_device) - 1]
        dev_C = devices[int(y_axis_device) - 1]
        # For testing purposes: Faking the position of each device to the ideal position.
        ideal_fused_data = FusedVarianceData(
            fused_distance_m=2.0,
            total_nodes=3,
            data_entries=[
                # Device A's perspective
                DeviceNodeStats(
                    scanning_device=dev_A,
                    data=[
                        NodeStats(
                            target_device=dev_B,
                            mean_m=2.0,
                            variance=0.01,
                            inverse_variance=100.0,
                            weight=0.5,
                        ),
                        NodeStats(
                            target_device=dev_C,
                            mean_m=2.0,
                            variance=0.01,
                            inverse_variance=100.0,
                            weight=0.5,
                        ),
                    ],
                ),
                # Device B's perspective
                DeviceNodeStats(
                    scanning_device=dev_B,
                    data=[
                        NodeStats(
                            target_device=dev_A,
                            mean_m=2.0,
                            variance=0.01,
                            inverse_variance=100.0,
                            weight=0.5,
                        ),
                        NodeStats(
                            target_device=dev_C,
                            mean_m=2.0,
                            variance=0.01,
                            inverse_variance=100.0,
                            weight=0.5,
                        ),
                    ],
                ),
                # Device C's perspective
                DeviceNodeStats(
                    scanning_device=dev_C,
                    data=[
                        NodeStats(
                            target_device=dev_A,
                            mean_m=2.0,
                            variance=0.01,
                            inverse_variance=100.0,
                            weight=0.5,
                        ),
                        NodeStats(
                            target_device=dev_B,
                            mean_m=2.0,
                            variance=0.01,
                            inverse_variance=100.0,
                            weight=0.5,
                        ),
                    ],
                ),
            ],
        )

        device_positions = generate_device_positions(
            ideal_fused_data,
            dev_A.device_id,
            dev_B.device_id,
            dev_C.device_id,
        )
    else:
        device_positions = [
            DevicePosition.from_DeviceData(
                device_data=devices[0], position=Position(0, 0)
            )
        ]

    ekf = EkfMultipleBadgesSequentialGatedWithInitialVelocity(device_positions)

    ekf_logger = DataLogger(
        [
            "device_id",
            "tracking_device_position_x",
            "tracking_device_position_y",
            "tracking_device_bluetooth_mac",
            "tracking_device_hostname",
            "tracking_device_ip_address",
            "technology",
            "tracked_device_raw_distance_data",
            "ekf_estimation_x",
            "ekf_estimation_xv",
            "ekf_estimation_y",
            "ekf_estimation_yv",
            "timestamp",
        ],
        name="Device_Updated_EKF_With_Values",
    )

    def incoming_data_handler(
        technology: TECHNOLOGY,
        estimated_distance: EstimatedDistance,
        device_id: DeviceId,
    ) -> None:
        print(f"Received data from {device_id}: {estimated_distance} ({technology})")
        ekf.add_measurement(device_id, estimated_distance)
        ekf_estimation = ekf.get_state()

        now_str = datetime.now(UTC).isoformat()

        # Get the device that sent the data based on the id it used to send the data.
        client = next(
            (pos for pos in device_positions if pos.device_id == device_id), None
        )

        if client is None:
            raise Exception("Found no known client of this udp package based on id!")

        ekf_logger.write_data_point(
            [
                client.device_id,
                client.position.x,
                client.position.y,
                client.bluetooth_mac,
                client.hostname,
                client.ip_address,
                str(technology),
                estimated_distance,
                ekf_estimation.x,
                ekf_estimation.vx,
                ekf_estimation.y,
                ekf_estimation.vy,
                now_str,
            ]
        )

        if update_website is not None:
            update_website(data={"x": ekf_estimation.x, "y": ekf_estimation.y})

    data_handler.subscribe(incoming_data_handler)
    data_handler.start()

    while True:
        await sleep(1000)


if __name__ == "__main__":
    asyncio.run(main())

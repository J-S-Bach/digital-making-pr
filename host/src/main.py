import asyncio
from asyncio import sleep
from datetime import UTC, datetime
from typing import NamedTuple

from src.calculate_relative_positions import (
    fuse_n_nodes_inverse_variance,
    generate_device_positions,
)
from src.data_logger import DataLogger
from src.estimation import DevicePosition, LiveEKFTracker, Position
from src.incoming_data_handler import (
    TECHNOLOGY,
    DeviceId,
    EstimatedDistance,
    UDPCatcher,
)
from src.self_identification import get_own_ip
from src.technology_handler import TechnologyHandler

from .discover_clients import DeviceData, discover_clients

devices = discover_clients()

UDP_PORT = 6969
own_ip = get_own_ip()
target_udp_address = f"http://{own_ip}:{UDP_PORT}"


async def main():
    if len(devices) == 0:
        print("No Device Could be found...")
        return

    data_handler = UDPCatcher(UDP_PORT)

    technology_handler = TechnologyHandler(devices, target_udp_address)

    position_estimations = technology_handler.scan_device_positions()

    technology_handler.activate_bluetooth()

    device_positions: list[DevicePosition] = []

    if position_estimations is not None:
        fused_nodes = fuse_n_nodes_inverse_variance(position_estimations)

        device_positions = generate_device_positions(fused_nodes)
    else:
        device_positions = [
            DevicePosition.from_DeviceData(
                device_data=devices[0], position=Position(0, 0)
            )
        ]

    ekf = LiveEKFTracker(device_positions)

    ekf_logger = DataLogger(
        [
            "device_id",
            "device_position_x",
            "device_position_y",
            "technology",
            "input_data",
            "ekf_estimation_x",
            "ekf_estimation_xv",
            "ekf_estimation_y",
            "ekf_estimation_yv",
            "timestamp",
        ],
        name="Device_Updated_EKF_With_Values",
    )

    def incoming_data_handler(
        technology: TECHNOLOGY, estimated: EstimatedDistance, device_id: DeviceId
    ) -> None:
        print(f"Received data from {device_id}: {estimated} ({technology})")
        ekf.ingest_measurement(device_id, estimated)
        ekf_estimation = ekf.get_state()

        d = datetime.now(UTC).isoformat()
        matching_device_position =  next((pos for pos in device_positions if pos.device_id == device_id), None)
        if matching_device_position is None:
            raise Exception("no matching device position found")

        ekf_logger.write_data_point(
            [
                device_id,
                matching_device_position.position.x,
                matching_device_position.position.y,
                str(technology),
                estimated,
                ekf_estimation.x,
                ekf_estimation.vx,
                ekf_estimation.y,
                ekf_estimation.vy,
                d,
            ]
        )

    data_handler.subscribe(incoming_data_handler)
    data_handler.start()

    while True:
        await sleep(1000)


if __name__ == "__main__":
    asyncio.run(main())

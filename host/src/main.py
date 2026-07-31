import asyncio
import socket
from asyncio import sleep
from calendar import calendar
from datetime import datetime

from src.data_logger import DataLogger
from src.estimation import LiveEKFTracker
from src.incoming_data_handler import (
    TECHNOLOGY,
    DeviceId,
    EstimatedDistance,
    IncomingDataHandler,
)
from src.self_identification import get_own_ip
from src.technology_handler import TechnologyHandler

from .discover_clients import discover_clients

devices = discover_clients()

UDP_PORT = 6969
own_ip = get_own_ip()
target_udp_address = f"http://{own_ip}:{UDP_PORT}"


async def main():
    data_handler = IncomingDataHandler(UDP_PORT)
    technology_handler = TechnologyHandler(devices, target_udp_address)
    technology_handler.calibrate_device_positions()
    technology_handler.activate_bluetooth()

    device_positions: dict[str, list[float]] = {
        x["device_id"]: [0.1, 0.1] for x in devices
    }
    ekf = LiveEKFTracker(device_positions)

    ekf_logger = DataLogger(
        [
            "device_id",
            "technology",
            "input_data",
            "ekf_estimation_x",
            "ekf_estimation_xv",
            "ekf_estimation_y",
            "ekf_estimation_yv",
            "timestamp",
        ]
    )

    def incoming_data_handler(
        technology: TECHNOLOGY, estimated: EstimatedDistance, device_id: DeviceId
    ) -> None:
        ekf.ingest_measurements({device_id: [estimated]})
        ekf_estimation = ekf.get_state()

        d = datetime.now().isoformat()
        ekf_logger.write_data_point(
            [
                device_id,
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


asyncio.run(main())

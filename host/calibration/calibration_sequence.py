import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

from src.discover_clients import discover_clients

console = Console()

calibration_distances = [50, 100, 150, 200]


def calibration_sequence():
    console.print(
        Panel.fit(
            "[bold cyan]Calibration Sequence",
            border_style="blue",
        )
    )
    devices = discover_clients()

    if len(devices) <= 0:
        print("No devices found!")
        return

    elif len(devices) == 1:
        console.print("1 device found. Therefore no selection necessary.")
        selected_device = devices[0]
    else:
        select_device_string = [
            f"-  {device.hostname} [{index + 1}]\n"
            for index, device in enumerate(devices)
        ]

        choice_str: str = Prompt.ask(
            f"Select a device:\n{''.join(select_device_string)}",
            choices=[str(index + 1) for index, _ in enumerate(devices)],
            default="auto",
        )
        selected_device = devices[int(choice_str) - 1]

    console.print(f"\n[bold yellow]Selected Device: {selected_device}")

    with Progress(
        SpinnerColumn(),
        TextColumn(f"[progress.description]Starting calibration sequence on esp32"),
        transient=True,
    ) as progress:
        progress.add_task("sampling", total=None)

        res = requests.post(
            "http://" + selected_device.ip_address + "/calibration/start",
        )

        res.raise_for_status()

    for calibration_distance in calibration_distances:
        _ = input(
            f"Press Enter when {selected_device.hostname} is in position and tracking device is {calibration_distance / 100} meters away."
        )
        with Progress(
            SpinnerColumn(),
            TextColumn(
                f"[progress.description]Sending bluetooth trackers on client..."
            ),
            transient=True,
        ) as progress:
            _ = progress.add_task("sampling", total=None)

            res = requests.post(
                "http://"
                + selected_device.ip_address
                + "/calibration/distance/"
                + str(calibration_distance),
                json={"scanningDeviceServiceUUID": "0xaaaa"},
            )

            res.raise_for_status()

    res = requests.post(
        "http://" + selected_device.ip_address + "/calibration/finish",
    )

    res.raise_for_status()

    console.print("Calibration sequence successful.")


if __name__ == "__main__":
    calibration_sequence()

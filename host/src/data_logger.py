import atexit
import csv
from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from time import time
from typing import TypeVarTuple

output_dir = Path("./tracker/")
Ts = TypeVarTuple("Ts")


class DataLogger[*Ts]:
    def __init__(self, header_row: list[str], name: str | None = None) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        self.file_name: str = f"{timestamp}_{name}.csv"

        output_dir.mkdir(parents=True, exist_ok=True)

        self.file: TextIOWrapper = open(output_dir / self.file_name, "w", newline="")
        self.csv_writer = csv.writer(self.file)

        # Initialize with given data.
        self.csv_writer.writerow(header_row)
        self.file.flush()

        # Release file gracefully.
        _ = atexit.register(self.close)

    def write_data_point(self, data: list[str | int | float]):
        self.csv_writer.writerow(data)
        self.file.flush()

    def close(self):
        if not self.file.closed:
            self.file.close()

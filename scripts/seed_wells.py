import csv
from pathlib import Path


def seed_wells() -> None:
    """Load valid well rows and report how many are ready for persistence."""

    data_file = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "processed"
        / "groundwater_data.csv"
    )
    if not data_file.exists():
        raise FileNotFoundError(f"Missing data file: {data_file}")

    with data_file.open(newline="", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        wells = [row for row in reader if row.get("sample_id")]
    print(f"Loaded {len(wells)} wells from {data_file}")


if __name__ == "__main__":
    seed_wells()
"""Inspect processed groundwater records before database seeding is implemented."""

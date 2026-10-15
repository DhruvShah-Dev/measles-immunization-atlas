"""Download WHO/UNICEF measles coverage estimates from the WHO GHO API."""

import argparse
import csv
from pathlib import Path

import requests


INDICATORS = {"MCV1": "WHS8_110", "MCV2": "MCV2"}
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--indicator", choices=INDICATORS, default="MCV1")
    indicator = parser.parse_args().indicator
    url = f"https://ghoapi.azureedge.net/api/{INDICATORS[indicator]}"
    output = OUTPUT_DIR / f"who_{indicator.lower()}_2019_2025.csv"
    params = {
        "$filter": "TimeDim ge 2019 and TimeDim le 2025",
        "$select": "SpatialDimType,SpatialDim,TimeDim,NumericValue",
        "$orderby": "TimeDim,SpatialDimType,SpatialDim",
        "$format": "json",
    }
    rows = []
    with requests.Session() as session:
        while url:
            response = session.get(url, params=params, timeout=60)
            response.raise_for_status()
            payload = response.json()
            rows.extend(payload["value"])
            url = payload.get("@odata.nextLink")
            params = None

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["SpatialDimType", "SpatialDim", "TimeDim", "NumericValue"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {output}")


if __name__ == "__main__":
    main()

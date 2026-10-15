"""Prepare compact Natural Earth country and admin1 outlines for the offline map.

Requires requests and npx (mapshaper is fetched by npx on first run).
Natural Earth data are public domain: https://www.naturalearthdata.com/about/terms-of-use/
"""

import csv
import json
import shutil
import subprocess
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "data" / "geo"
SOURCE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
ALIASES = {"SDS": "SSD", "PSX": "PSE"}  # Natural Earth -> WHO ISO3


def read_source(name: str) -> dict:
    path = GEO / name
    if not path.exists():
        response = requests.get(SOURCE + name, timeout=120)
        response.raise_for_status()
        path.write_bytes(response.content)
    return json.loads(path.read_text(encoding="utf-8"))


def slim(features: list[dict], key: str, codes: set[str], name_key: str) -> dict:
    selected = []
    for feature in features:
        natural_code = feature["properties"].get(key)
        iso3 = ALIASES.get(natural_code, natural_code)
        if iso3 not in codes:
            continue
        selected.append({
            "type": "Feature",
            "properties": {"iso3": iso3, "name": feature["properties"].get(name_key) or iso3},
            "geometry": feature["geometry"],
        })
    return {"type": "FeatureCollection", "features": selected}


def simplify(source: Path, output: Path, percent: str) -> None:
    npx = shutil.which("npx.cmd") or shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required to run mapshaper")
    subprocess.run([
        npx, "--yes", "mapshaper@0.7.87", str(source), "-simplify", percent,
        "keep-shapes", "-o", "precision=0.001", str(output),
    ], check=True, timeout=180)


def main() -> None:
    GEO.mkdir(parents=True, exist_ok=True)
    with (ROOT / "data/processed/country_screen_2025.csv").open(encoding="utf-8", newline="") as file:
        codes = {row["iso3"] for row in csv.DictReader(file)}
    inputs = [
        ("ne_50m_admin_0_countries.geojson", "ADM0_A3", "NAME", "world", "35%"),
        ("ne_10m_admin_1_states_provinces.geojson", "adm0_a3", "name", "admin1", "8%"),
    ]
    for source_name, key, name_key, stem, percent in inputs:
        source = read_source(source_name)
        collection = slim(source["features"], key, codes, name_key)
        matched = {feature["properties"]["iso3"] for feature in collection["features"]}
        if matched != codes:
            raise ValueError(f"{stem} missing WHO codes: {sorted(codes - matched)}")
        temporary = GEO / f"_{stem}_input.geojson"
        output = GEO / f"{stem}_simplified.geojson"
        temporary.write_text(json.dumps(collection, ensure_ascii=False), encoding="utf-8")
        try:
            simplify(temporary, output, percent)
        finally:
            temporary.unlink(missing_ok=True)
        result = json.loads(output.read_text(encoding="utf-8"))
        if len(result["features"]) != len(collection["features"]):
            raise ValueError(f"Simplification changed {stem} feature count")
        print(f"{stem}: {len(result['features'])} shapes, {output.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()

"""Build a self-contained, offline WHO measles evidence dashboard."""

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"


def read(path: str) -> list[dict]:
    with (ROOT / path).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def numeric(value: str) -> int | float | None:
    if value == "":
        return None
    result = float(value)
    return int(result) if result.is_integer() else result


def main() -> None:
    countries = read("data/processed/country_screen_2025.csv")
    regions = read("data/processed/region_screen_2025.csv")
    coverage = []
    for dose in ("mcv1", "mcv2"):
        for row in read(f"data/raw/who_{dose}_2019_2025.csv"):
            coverage.append({
                "kind": row["SpatialDimType"],
                "code": row["SpatialDim"],
                "year": int(row["TimeDim"]),
                "dose": dose.upper(),
                "value": numeric(row["NumericValue"]),
            })
    case_index = {}
    for row in read("data/raw/who_measles_reported_cases_2019_2025.csv"):
        key = (row["GROUP"], row["CODE"], int(row["YEAR"]))
        case_index[key] = {"group": key[0], "code": key[1], "year": key[2],
                           "cases": numeric(row["CASES"]), "incidence": None}
    for row in read("data/raw/who_measles_incidence_2019_2025.csv"):
        key = (row["GROUP"], row["CODE"], int(row["YEAR"]))
        if key not in case_index:
            raise ValueError(f"Incidence has no case row: {key}")
        case_index[key]["incidence"] = numeric(row["INCIDENCE_RATE"])
    for row in countries:
        for key, value in list(row.items()):
            if key.endswith(("_pct", "_pp", "_count", "_total")):
                row[key] = numeric(value)
    for row in regions:
        for key, value in list(row.items()):
            if key not in ("who_region", "region"):
                row[key] = numeric(value)
    data = {"countries": countries, "regions": regions, "coverage": coverage,
            "cases": list(case_index.values()), "snapshot": "2026-10-15"}
    world = json.loads((ROOT / "data/geo/world_simplified.geojson").read_text(encoding="utf-8"))
    admin1 = json.loads((ROOT / "data/geo/admin1_simplified.geojson").read_text(encoding="utf-8"))
    if len(world["features"]) != 195 or len(admin1["features"]) < 4300:
        raise ValueError("Unexpected map boundary shape")
    data["mapWorld"] = world
    data["mapAdmin1"] = admin1
    if len(countries) != 195 or len(regions) != 6 or len(coverage) != 2884:
        raise ValueError("Unexpected coverage shape")
    if len(data["cases"]) != 1491:
        raise ValueError("Unexpected case shape")
    html = (APP / "index.html").read_text(encoding="utf-8")
    style = (APP / "style.css").read_text(encoding="utf-8")
    map_style = (APP / "map.css").read_text(encoding="utf-8")
    script = (APP / "app.js").read_text(encoding="utf-8")
    map_script = (APP / "map.js").read_text(encoding="utf-8")
    leaflet_style = (APP / "vendor/leaflet.css").read_text(encoding="utf-8")
    leaflet_script = (APP / "vendor/leaflet.js").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = html.replace("/* INLINE_LEAFLET_STYLE */", leaflet_style)
    html = html.replace("/* INLINE_STYLE */", style).replace("/* INLINE_SCRIPT */", script)
    html = html.replace("/* INLINE_MAP_STYLE */", map_style)
    html = html.replace("/* INLINE_LEAFLET_SCRIPT */", leaflet_script)
    html = html.replace("/* INLINE_MAP_SCRIPT */", map_script)
    html = html.replace("/* INLINE_DATA */", payload)
    output = ROOT / "dashboard.html"
    output.write_text(html, encoding="utf-8")
    print(f"Built {output} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

"""Check the committed WHO snapshot and geographic joins before publishing."""

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def rows(relative: str) -> list[dict]:
    with (ROOT / relative).open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def unique(data: list[dict], fields: tuple[str, ...], label: str) -> None:
    keys = [tuple(row[field] for field in fields) for row in data]
    assert len(keys) == len(set(keys)), f"Duplicate {label} key"


def main() -> None:
    countries = rows("data/processed/country_screen_2025.csv")
    regions = rows("data/processed/region_screen_2025.csv")
    assert len(countries) == 195 and len(regions) == 6
    unique(countries, ("iso3",), "country")
    unique(regions, ("who_region",), "region")
    codes = {row["iso3"] for row in countries}
    region_codes = {row["who_region"] for row in regions}
    assert all(row["who_region"] in region_codes for row in countries)
    assert sum(int(float(row["countries"])) for row in regions) == 195

    for dose in ("mcv1", "mcv2"):
        coverage = rows(f"data/raw/who_{dose}_2019_2025.csv")
        assert len(coverage) == 1442
        unique(coverage, ("SpatialDimType", "SpatialDim", "TimeDim"), dose)
        assert {row["TimeDim"] for row in coverage} == {str(year) for year in range(2019, 2026)}
        assert all(0 <= float(row["NumericValue"]) <= 100 for row in coverage)
        assert {row["SpatialDim"] for row in coverage if row["SpatialDimType"] == "COUNTRY"} == codes

    assert sum(float(row["mcv1_2025_pct"]) < 80 for row in countries) == 49
    assert sum(float(row["mcv1_2025_pct"]) < 95 for row in countries) == 132
    assert sum(float(row["mcv1_change_pp"]) < 0 for row in countries) == 115
    assert Counter(row["district_mcv1_quality"] for row in countries) == {
        "corroborated": 102,
        "missing_percent": 55,
        "inconsistent_count_or_denominator": 28,
        "unverified_denominator": 10,
    }

    case_rows = rows("data/raw/who_measles_reported_cases_2019_2025.csv")
    rate_rows = rows("data/raw/who_measles_incidence_2019_2025.csv")
    assert len(case_rows) == len(rate_rows) == 1491
    key = lambda row: (row["GROUP"], row["CODE"], row["YEAR"])
    unique(case_rows, ("GROUP", "CODE", "YEAR"), "cases")
    unique(rate_rows, ("GROUP", "CODE", "YEAR"), "incidence")
    assert {key(row) for row in case_rows} == {key(row) for row in rate_rows}
    cases_2025 = {row["CODE"]: row["CASES"] for row in case_rows if row["GROUP"] == "COUNTRIES" and row["YEAR"] == "2025"}
    assert sum(cases_2025.get(code, "") != "" for code in codes) == 183
    assert any(cases_2025.get(code) == "0" for code in codes), "Published zeroes must remain distinct from missing reports"

    for stem in ("world", "admin1"):
        geo = json.loads((ROOT / f"data/geo/{stem}_simplified.geojson").read_text(encoding="utf-8"))
        shapes = geo["features"]
        assert {feature["properties"]["iso3"] for feature in shapes} == codes
        assert len(shapes) == (195 if stem == "world" else 4386)

    dashboard = (ROOT / "dashboard.html").read_text(encoding="utf-8")
    assert "/* INLINE_DATA */" not in dashboard
    assert "Named district records require a separate WHO data request" in dashboard
    print("Snapshot valid: 195 countries, 6 regions, 2 coverage series, 1,491 case rows, and 4,386 province/state outlines")


if __name__ == "__main__":
    main()

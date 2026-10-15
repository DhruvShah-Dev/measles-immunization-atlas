"""Build country and regional measles coverage screens from WHO CSV snapshots."""

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
REGIONS = {
    "AFRO": ("AFR", "African Region"),
    "AMRO": ("AMR", "Region of the Americas"),
    "EMRO": ("EMR", "Eastern Mediterranean Region"),
    "EURO": ("EUR", "European Region"),
    "SEARO": ("SEAR", "South-East Asia Region"),
    "WPRO": ("WPR", "Western Pacific Region"),
}


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def number(value: str | None) -> float | None:
    try:
        return float(value) if value not in (None, "", "ND", "NR") else None
    except ValueError:
        return None


def display(value: float | None) -> str:
    return "" if value is None else f"{value:.2f}".rstrip("0").rstrip(".")


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {path}")


def district_metrics(values: dict[str, str], dose: str) -> dict[str, str]:
    percent = number(values.get(f"CALC_DIST_95{dose}_P"))
    count = number(values.get(f"DIST_95_NUMBER_DISTRICTS_{dose}"))
    total = number(values.get("DIST_TOTAL_NUMBER"))
    if percent is None:
        quality = "missing_percent"
    elif not 0 <= percent <= 100:
        quality = "invalid_percent"
    elif count is None or total is None or total <= 0:
        quality = "unverified_denominator"
    elif abs(percent - 100 * count / total) > 1:
        quality = "inconsistent_count_or_denominator"
    else:
        quality = "corroborated"
    prefix = f"district_{dose.lower()}"
    return {
        f"{prefix}_at_least_95_pct": display(percent),
        f"{prefix}_at_least_95_count": display(count),
        f"{prefix}_total": display(total),
        f"{prefix}_quality": quality,
    }


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    lookup_rows = read_csv(RAW / "who_country_lookup.csv")
    lookup = {row["ISO_3_CODE"]: row for row in lookup_rows}
    if len(lookup) != len(lookup_rows):
        raise ValueError("Duplicate country lookup codes")
    gho_lookup_rows = read_csv(RAW / "who_gho_country_lookup.csv")
    gho_lookup = {row["Code"]: row for row in gho_lookup_rows}
    if len(gho_lookup) != len(gho_lookup_rows):
        raise ValueError("Duplicate GHO country lookup codes")

    indicator_data: dict[str, dict[tuple[str, str, int], float]] = {}
    for dose in ("mcv1", "mcv2"):
        rows = read_csv(RAW / f"who_{dose}_2019_2025.csv")
        index = {}
        for row in rows:
            key = (row["SpatialDimType"], row["SpatialDim"], int(row["TimeDim"]))
            if key in index:
                raise ValueError(f"Duplicate {dose} key: {key}")
            index[key] = float(row["NumericValue"])
        indicator_data[dose] = index

    raw_districts = read_csv(RAW / "who_district_summary_2025.csv")
    district_by_country = defaultdict(dict)
    for row in raw_districts:
        values = district_by_country[row["ISO_3_CODE"]]
        if row["INDCODE"] in values:
            raise ValueError(f"Duplicate district indicator: {row['ISO_3_CODE']} {row['INDCODE']}")
        values[row["INDCODE"]] = row["VALUE"]

    country_codes = sorted(
        key[1] for key in indicator_data["mcv1"] if key[0] == "COUNTRY" and key[2] == 2025
    )
    if len(country_codes) != 195 or len(set(country_codes)) != 195:
        raise ValueError("Expected 195 unique 2025 countries")
    countries = []
    for iso in country_codes:
        if iso not in lookup:
            raise ValueError(f"Country missing from WHO lookup: {iso}")
        if iso not in gho_lookup:
            raise ValueError(f"Country missing from GHO lookup: {iso}")
        meta = lookup[iso]
        gho_meta = gho_lookup[iso]
        region = meta["WHO_REGION"]
        if region not in REGIONS:
            raise ValueError(f"Unknown WHO region for {iso}: {region}")
        if REGIONS[region][0] != gho_meta["ParentCode"]:
            raise ValueError(f"WHO region mismatch for {iso}")
        mcv1_2019 = indicator_data["mcv1"][("COUNTRY", iso, 2019)]
        mcv1_2025 = indicator_data["mcv1"][("COUNTRY", iso, 2025)]
        mcv2_2019_raw = indicator_data["mcv2"][("COUNTRY", iso, 2019)]
        mcv2_2025_raw = indicator_data["mcv2"][("COUNTRY", iso, 2025)]
        # WHO's 2025 revision produces MCV2 estimates for 193 countries.
        # Keep API zeroes visible as review flags, not comparable rankings.
        mcv2_2019 = mcv2_2019_raw if mcv2_2019_raw > 0 else None
        mcv2_2025 = mcv2_2025_raw if mcv2_2025_raw > 0 else None
        district = district_by_country.get(iso, {})
        countries.append(
            {
                "iso3": iso,
                "country": gho_meta["Title"],
                "who_region": region,
                "mcv1_2019_pct": display(mcv1_2019),
                "mcv1_2025_pct": display(mcv1_2025),
                "mcv1_change_pp": display(mcv1_2025 - mcv1_2019),
                "mcv2_2019_pct": display(mcv2_2019),
                "mcv2_2025_pct": display(mcv2_2025),
                "mcv2_change_pp": display(
                    mcv2_2025 - mcv2_2019 if mcv2_2025 is not None and mcv2_2019 is not None else None
                ),
                "mcv2_2025_status": "estimate" if mcv2_2025 is not None else "zero_value_check_schedule",
                **district_metrics(district, "MCV1"),
                **district_metrics(district, "MCV2"),
            }
        )
    countries.sort(key=lambda row: (float(row["mcv1_2025_pct"]), row["country"]))
    country_fields = list(countries[0])
    write_csv(PROCESSED / "country_screen_2025.csv", countries, country_fields)

    regions = []
    for code, (gho_code, name) in REGIONS.items():
        members = [row for row in countries if row["who_region"] == code]
        mcv1 = indicator_data["mcv1"]
        mcv2 = indicator_data["mcv2"]
        regions.append(
            {
                "who_region": code,
                "region": name,
                "countries": len(members),
                "mcv1_2019_pct": display(mcv1[("REGION", gho_code, 2019)]),
                "mcv1_2025_pct": display(mcv1[("REGION", gho_code, 2025)]),
                "mcv2_2019_pct": display(mcv2[("REGION", gho_code, 2019)]),
                "mcv2_2025_pct": display(mcv2[("REGION", gho_code, 2025)]),
                "countries_mcv1_below_80": sum(float(row["mcv1_2025_pct"]) < 80 for row in members),
                "countries_mcv1_below_95": sum(float(row["mcv1_2025_pct"]) < 95 for row in members),
                "countries_with_corroborated_district_mcv1_summary": sum(
                    row["district_mcv1_quality"] == "corroborated" for row in members
                ),
            }
        )
    write_csv(PROCESSED / "region_screen_2025.csv", regions, list(regions[0]))


if __name__ == "__main__":
    main()

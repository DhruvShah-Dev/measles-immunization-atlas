"""Download WHO's public 2025 country-level district coverage summaries."""

import csv
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
API = "https://xmart-api-public.who.int/WIISE"


def fetch_rows(session: requests.Session, resource: str, params: dict) -> list[dict]:
    rows = []
    offset = 0
    page_size = 5000
    total = None
    while total is None or offset < total:
        response = session.get(
            f"{API}/{resource}",
            params={**params, "$top": page_size, "$skip": offset, "$count": "true"},
            timeout=90,
        )
        response.raise_for_status()
        payload = response.json()
        if total is None:
            total = payload["@odata.count"]
        batch = payload["value"]
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
    if len(rows) != total:
        raise RuntimeError(f"Incomplete API response: {len(rows)} of {total} rows")
    return rows


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in fields} for row in rows)
    print(f"Saved {len(rows)} rows to {path}")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    with requests.Session() as session:
        country_fields = ["ISO_3_CODE", "COUNTRYNAME", "WHO_REGION", "WHOMEMBER"]
        countries = fetch_rows(
            session,
            "V_LIST_COUNTRIES",
            {"$select": ",".join(country_fields), "$orderby": "ISO_3_CODE"},
        )
        gho_response = session.get(
            "https://ghoapi.azureedge.net/api/DIMENSION/COUNTRY/DimensionValues",
            timeout=60,
        )
        gho_response.raise_for_status()
        gho_countries = gho_response.json()["value"]
        summary_fields = [
            "YEAR", "ISO_3_CODE", "COUNTRYNAME", "WHO_REGION", "INDCODE", "DESCRIPTION", "VALUE"
        ]
        summaries = fetch_rows(
            session,
            "MT_AD_IND_LONG",
            {
                "$filter": "INDCATCODE eq 'SYSTEM_PERFORMANCE' and YEAR eq 2025 "
                "and (contains(INDCODE,'MCV1') or contains(INDCODE,'MCV2') "
                "or INDCODE eq 'DIST_TOTAL_NUMBER' "
                "or INDCODE eq 'CALC_COMPLETENESS_PERCENT')",
                "$select": ",".join(summary_fields),
                "$orderby": "ISO_3_CODE,INDCODE",
            },
        )
    write_csv(RAW / "who_country_lookup.csv", countries, country_fields)
    write_csv(
        RAW / "who_gho_country_lookup.csv",
        gho_countries,
        ["Code", "Title", "ParentCode"],
    )
    write_csv(RAW / "who_district_summary_2025.csv", summaries, summary_fields)


if __name__ == "__main__":
    main()

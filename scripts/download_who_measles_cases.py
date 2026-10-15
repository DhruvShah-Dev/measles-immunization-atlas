"""Download public WHO measles reported cases and incidence, 2019–2025."""

import csv
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
API = "https://xmart-api-public.who.int/WIISE"
FILTER = "DISEASE eq 'MEASLES' and YEAR ge 2019 and YEAR le 2025"


def fetch(session: requests.Session, table: str, fields: list[str]) -> list[dict]:
    rows = []
    total = None
    while total is None or len(rows) < total:
        response = session.get(
            f"{API}/{table}",
            params={
                "$filter": FILTER,
                "$select": ",".join(fields),
                "$orderby": "GROUP,CODE,YEAR",
                "$top": 5000,
                "$skip": len(rows),
                "$count": "true",
            },
            timeout=90,
        )
        response.raise_for_status()
        payload = response.json()
        total = payload["@odata.count"]
        batch = payload["value"]
        if not batch:
            break
        rows.extend(batch)
    if len(rows) != total:
        raise RuntimeError(f"Incomplete {table}: {len(rows)} of {total}")
    keys = [(row["GROUP"], row["CODE"], row["YEAR"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError(f"Duplicate geography-year in {table}")
    return rows


def save(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in fields} for row in rows)
    print(f"Saved {len(rows)} rows to {path}")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    with requests.Session() as session:
        cases_fields = ["GROUP", "CODE", "NAME", "YEAR", "CASES"]
        rate_fields = ["GROUP", "CODE", "NAME", "YEAR", "DENOMINATOR", "INCIDENCE_RATE"]
        cases = fetch(session, "MT_AD_INC_LONG", cases_fields)
        rates = fetch(session, "MT_AD_INC_RATE_LONG", rate_fields)
    save(RAW / "who_measles_reported_cases_2019_2025.csv", cases, cases_fields)
    save(RAW / "who_measles_incidence_2019_2025.csv", rates, rate_fields)


if __name__ == "__main__":
    main()

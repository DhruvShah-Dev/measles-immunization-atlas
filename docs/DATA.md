# Data provenance and interpretation

## Snapshot

The reference extracts were downloaded on **15 October 2026** and cover **2019–2025**. The public repository does not redistribute the WHO CSVs or generated dashboard. Run the download and build scripts to make a local copy. WHO can revise estimates and surveillance reports, so a later download may differ from the reference findings.

| Dataset | Source | Scope and project file |
| --- | --- | --- |
| MCV1 national/regional/global coverage | [WHO GHO OData API](https://www.who.int/data/gho/info/gho-odata-api), indicator `WHS8_110` | 1,442 geography-year rows in `data/raw/who_mcv1_2019_2025.csv` |
| MCV2 national/regional/global coverage | WHO GHO OData API, indicator `MCV2` | 1,442 rows in `data/raw/who_mcv2_2019_2025.csv` |
| District coverage-band summaries | [WHO System Performance](https://immunizationdata.who.int/global/wiise-detail-page/system-performance) public API | 7,585 indicator rows in `data/raw/who_district_summary_2025.csv`; no district names |
| Measles reported cases and incidence | [WHO Immunization Data portal](https://immunizationdata.who.int/global/wiise-detail-page/measles-reported-cases-and-incidence) public API | 1,491 geography-year rows per measure in `data/raw/who_measles_reported_cases_2019_2025.csv` and `who_measles_incidence_2019_2025.csv` |
| Boundary reference | [Natural Earth](https://www.naturalearthdata.com/) | 195 country outlines and 4,386 province/state outlines in `data/geo/` |

The 195-country comparison joins ISO3 codes from the GHO coverage data with WHO country and region lookup tables. Natural Earth's `SDS` and `PSX` geometry codes are matched to `SSD` and `PSE` in the WHO screen. Boundary geometry is not WHO coverage data, and borders may differ from national or WHO conventions.

## Main fields and decisions

- **MCV1 / MCV2 percentage:** WHO/UNICEF estimated national coverage of the respective routine measles dose. MCV2 target ages vary by country. A zero MCV2 API entry is flagged for country schedule review and left unavailable in the processed comparison.
- **Percentage-point change:** 2025 percentage minus 2019 percentage from the same downloaded WHO revision.
- **District summary percentage:** WHO's public country-level percentage of reported districts in the ≥95% coverage band. This is administrative reporting and is distinct from the national WHO/UNICEF estimate.
- **District quality flag:** The published district-band percentage is considered *arithmetically corroborated* if it agrees within one percentage point with the published count divided by the reported district total. This checks internal arithmetic only. Missing, invalid, inconsistent, and unverified values are flagged separately.
- **Reported measles cases / incidence:** Surveillance measures, displayed separately from coverage. A blank report is missing, while a published zero remains zero. Incidence is per million total population. Reporting coverage and surveillance sensitivity can change across countries and years.
- **Priority shortlist:** An unweighted country screen using user-visible thresholds for low MCV1, decline, and corroborated district summaries. It does not estimate missed-child counts or predict outbreaks.

The map's province/state outlines carry **no local MCV1 or MCV2 values**. WHO says the named subnational coverage dataset requires a [data request](https://immunizationdata.who.int/docs/librariesprovider21/additional-datasets/how-to-access-more-data.pdf?sfvrsn=ee878941_1). Matching any later extract to boundaries will require checking administrative level, area identifiers, reporting year, numerator, and denominator.

## Use and attribution

WHO's [dataset terms](https://www.who.int/about/policies/publishing/data-policy/terms-and-conditions) govern the WHO extracts and presentations of data derived from them. They require attribution to WHO and reporting countries and prohibit implying WHO endorsement. They also place conditions on alteration and reuse. The project's MIT license applies only to original code and original documentation; it does **not** relicense WHO data or Leaflet.

Suggested source line when reusing a result: **World Health Organization, WHO/UNICEF estimates of national immunization coverage and WHO Immunization Data public extracts, 2025 reference year, accessed 15 October 2026; underlying country reports acknowledged through WHO source metadata. Analysis and visualizations by this independent project.** Check the source page for country-specific attribution and current terms before republication.

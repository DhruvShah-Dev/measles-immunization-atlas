# WHO data: measles immunization gap

**Question:** Can WHO data be downloaded, and what healthcare problem does it reveal?

**Answer:** Yes. WHO's Global Health Observatory (GHO) OData API provides downloadable indicator records. The accompanying CSV contains the WHO/UNICEF estimate for first-dose measles-containing vaccine (MCV1) coverage, 2019–2025. It reveals a persistent gap in routine childhood immunization, especially in lower-income settings.

## Evidence

| MCV1 coverage | 2019 | 2025 | Change |
| --- | ---: | ---: | ---: |
| Global | 86% | 84% | −2 percentage points |
| WHO African Region | 72% | 71% | −1 percentage point |
| Low-income countries | 71% | 69% | −2 percentage points |
| High-income countries | 94% | 93% | −1 percentage point |

The 2025 low-income versus high-income gap is **24 percentage points**. Across the 195 countries in the download, 49 have MCV1 coverage below 80% in 2025. These country counts are unweighted: they do not measure the number of children affected.

WHO and UNICEF report that 2025 global MCV1 coverage was 84% and second-dose coverage was 77%. Both are below the 95% coverage level needed in every community to prevent measles outbreaks. They report large or disruptive measles outbreaks in 57 countries in 2025. These facts support the problem statement; this dataset alone does not establish that a specific local outbreak was caused by a specific coverage gap.

## Healthcare problem to investigate

**Children are missing routine measles vaccination, leaving communities vulnerable to preventable outbreaks.** A practical healthcare question is: *Where are children least likely to receive their first measles dose, and which local barriers prevent them from completing vaccination?*

National coverage identifies broad priorities. To choose outreach locations, pair it with district-level coverage, target-child counts, vaccination service access, and case surveillance. Measure improvement in local MCV1 and MCV2 coverage and the number of missed children reached.

## Data and limits

- CSV: `../data/raw/who_mcv1_2019_2025.csv`; 1,442 rows, 206 per year, comprising 195 countries, six WHO regions, four income groups, and the global estimate. No missing coverage values or duplicate year/location pairs were found.
- Reproduce: `python scripts/download_who_mcv1.py` from the repository root. Indicator code: `WHS8_110`. Coverage values are percentages, and the file retains WHO's location codes.
- For second-dose coverage, run `python scripts/download_who_mcv1.py --indicator MCV2`; this writes `../data/raw/who_mcv2_2019_2025.csv` using GHO indicator `MCV2`. See the [pre-ideation problem brief](06_who_measles_problem_definition.md) for the combined framing and measurement plan.
- WHO/UNICEF coverage values are estimates based on administrative data, surveys, and expert review. Some 2025 country estimates use earlier data where reporting was unavailable; underlying data quality differs by country. Historical estimates are revised each release, so compare years within this same downloaded revision.
- MCV1 measures first-dose coverage among 1-year-olds. It does not measure second-dose completion, individual immunity, or district-level equity. The WHO/UNICEF 95% benchmark applies to **each community**, so a national average above 95% cannot rule out local gaps.

## Sources

- [WHO GHO OData API documentation](https://www.who.int/data/gho/info/gho-odata-api)
- [WHO GHO MCV1 indicator data](https://ghoapi.azureedge.net/api/WHS8_110)
- [WHO/UNICEF 2025 immunization estimates and measles outbreak summary](https://www.who.int/news/item/15-07-2026-global-childhood-immunization-coverage-inches-forward-despite-conflict-and-hesitancy---unicef--who)
- [WHO/UNICEF estimates methodology and limitations](https://www.who.int/news-room/questions-and-answers/item/who-unicef-estimates-of-national-immunization-coverage)

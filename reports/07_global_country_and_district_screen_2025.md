# Global measles vaccination coverage screen, 2025

**Snapshot:** WHO/UNICEF 2025 revision, downloaded 15 October 2026.  
**Purpose:** Compare all available countries and WHO regions, then use public district summaries where the published values pass basic arithmetic checks.  
**Local outputs after running the scripts:** `data/processed/country_screen_2025.csv` (195 countries) and `data/processed/region_screen_2025.csv` (six WHO regions). WHO extracts and processed CSVs are not redistributed in the public repository.

## Main finding

The 2025 WHO/UNICEF estimates show an uneven measles vaccination gap across the world. First-dose (MCV1) coverage was **84% globally** and second-dose (MCV2) coverage was **77%**. The African Region had the lowest regional estimates: **71% MCV1** and **58% MCV2**. Across the 195 country records, **49** had MCV1 below 80%, **132** had MCV1 below 95%, and **115** had lower MCV1 than in 2019. These country counts are unweighted; they do not rank the number of children missed. [WHO immunization data portal](https://immunizationdata.who.int/global/wiise-detail-page/measles-vaccination-coverage); [WHO/UNICEF estimates methodology](https://www.who.int/news-room/questions-and-answers/item/who-unicef-estimates-of-national-immunization-coverage)

## Regional comparison

Regional percentages below are WHO/UNICEF regional estimates, weighted using target populations. They are **not** averages of the country percentages. The final column counts countries in the downloaded national MCV1 dataset.

| WHO region | MCV1 2019 | MCV1 2025 | MCV2 2025 | Countries with MCV1 <80% / all countries |
| --- | ---: | ---: | ---: | ---: |
| African Region | 72% | 71% | 58% | 20 / 47 |
| Region of the Americas | 87% | 88% | 78% | 5 / 35 |
| Eastern Mediterranean Region | 82% | 81% | 76% | 7 / 22 |
| European Region | 94% | 92% | 89% | 8 / 53 |
| South-East Asia Region | 95% | 96% | 93% | 2 / 10 |
| Western Pacific Region | 94% | 89% | 86% | 7 / 28 |

The South-East Asia regional average exceeds 95% for MCV1, but this does not show that every community meets the benchmark. WHO recommends sustained coverage of at least 95% with **both doses in every community**. [WHO measles guidance](https://www.who.int/emergencies/disease-outbreak-news/item/2025-DON561)

## Public district summary: what can be used

WHO's public [System performance](https://immunizationdata.who.int/global/wiise-detail-page/system-performance) dataset reports, by country, the percentage and number of districts in MCV1 and MCV2 coverage bands. It does **not** identify individual districts. The project downloaded 7,585 2025 indicator records spanning 205 WHO reporting entities; 195 of those entities are in the national comparison. Its country-level district summaries are **reported administrative data**, while the national percentages above are **WHO/UNICEF estimates**. The measures should be compared as signals of possible local gaps, not treated as the same measurement series.

For MCV1 in the 195-country screen:

| Published 2025 district summary status | Countries |
| --- | ---: |
| Percentage at ≥95% agrees within 1 percentage point with published count ÷ district total | 102 |
| Percentage missing | 55 |
| Percentage and count/total disagree by more than 1 point | 28 |
| Percentage present, but count or total unavailable | 10 |

**Example of why a national average is insufficient:** Nepal's national MCV1 estimate is **96%**, yet its public district summary says **19 of 77 districts (24.68%)** had reported MCV1 coverage of at least 95%. The published count and percentage agree arithmetically. This warrants local investigation; it does not establish that the remaining districts have the same number of missed children or that the administrative denominators are accurate. [WHO national coverage portal](https://immunizationdata.who.int/global/wiise-detail-page/measles-vaccination-coverage?ANTIGEN=MCV1&CODE=NPL); [WHO system performance](https://immunizationdata.who.int/global/wiise-detail-page/system-performance?ISO_3_CODE=NPL)

Among the 102 countries with arithmetically corroborated MCV1 district summaries, 66 report that fewer than half of their districts reached the 95% MCV1 band. This subset is **not representative of all countries or children**: countries have different numbers and sizes of districts, and data completeness varies. No global count of missed children or high-risk districts is inferred from it.

## Data quality and interpretation

- The two national CSVs have 1,442 rows each, with one value per geographic unit and year for 2019–2025. The 195 country codes join to the WHO country and region lookups without loss or duplication.
- The 2025 WHO/UNICEF revision produces MCV2 estimates for **193** countries. Two GHO country rows contain zero MCV2 values; the processed screen flags these for vaccine-schedule review and excludes them from MCV2 rankings rather than assuming actual zero coverage. [WHO 2025 revision notes](https://www.who.int/docs/default-source/immunization/immunization-coverage/wuenic_notes.pdf)
- The 7,585 district-summary records have unique reporting-entity/indicator keys. Missing values, `ND`, and `NR` are treated as unavailable. Published district percentages outside 0–100 would fail validation; none of the MCV1 ≥95% values in the 195-country screen did.
- “Arithmetically corroborated” only means the published percentage is within 1 percentage point of the published count divided by the published district total. It does not validate the vaccination numerator, population denominator, boundaries, or reporting completeness. The WHO subnational data have known variation in administrative levels and denominator quality. [WHO subnational overview](https://www.who.int/teams/immunization-vaccines-and-biologicals/Immunization-data-and-decision-making/global-monitoring/immunization-coverage/subnational-immunization-coverage-data); [WHO subnational limitations](https://cdn.who.int/media/docs/default-source/immunization/data_statistics/limitations.pdf)
- MCV1 and MCV2 target different age cohorts under local schedules. Their percentages must not be subtracted to claim individual dropout. Country values are coverage rates, not numbers of children missed; a population denominator is needed for volume-based prioritization.

## Boundary on named-district analysis

WHO states that its detailed **subnational coverage dataset is unpublished** and must be requested through its data-sharing process. The public summaries support country-level statements *about district bands*, but do not show which named districts are below target. A named-district map, district rankings, or district-level solution plan requires an approved detailed WHO extract or relevant national programme data. This is a source-access gap, not a missing computation. [WHO: How to Access More Data](https://immunizationdata.who.int/docs/librariesprovider21/additional-datasets/how-to-access-more-data.pdf?sfvrsn=ee878941_1)

## How to use the screen

1. Use the generated `data/processed/country_screen_2025.csv` to compare all 195 countries by MCV1 level, MCV1 change since 2019, MCV2 level where an estimate exists, and the availability and arithmetic status of district summaries.
2. Use the generated `data/processed/region_screen_2025.csv` to compare the six population-weighted WHO regional estimates and the number of countries below 80% MCV1.
3. For places selected for deeper work, obtain named-district coverage, target-child counts, case surveillance, schedule information, and programme context before deciding between routine-service, follow-up, campaign, and community-engagement options in the [problem brief](06_who_measles_problem_definition.md).

## Reproduce

From the repository root:

```powershell
python -m pip install -r requirements.txt
python scripts/download_who_mcv1.py
python scripts/download_who_mcv1.py --indicator MCV2
python scripts/download_who_system_performance.py
python scripts/build_global_screen.py
```

The WHO/UNICEF coverage revision and public administrative data can change on later downloads. Preserve this snapshot when comparing the report's numbers.
